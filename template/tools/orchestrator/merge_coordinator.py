#!/usr/bin/env python3
"""
Merge Coordinator

Handles PR merging with:
- Sequential merge queue (prevents race conditions)
- Conflict detection & resolution
- Test failure handling
- Retry mechanism
- Branch cleanup
"""

import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from threading import Thread, Lock

logger = logging.getLogger(__name__)


class MergeCoordinator:
    """
    Coordinates PR merging to prevent conflicts and ensure clean workflow
    """

    def __init__(self, redis_client, config, project_root="/app"):
        self.redis = redis_client
        self.config = config
        self.project_root = Path(project_root)
        self.merge_lock = Lock()
        self.merge_queue_key = "orchestrator:merge_queue"
        self.active_merges_key = "orchestrator:active_merges"

        # Start merge worker thread
        self.running = True
        self.worker_thread = Thread(target=self._merge_worker, daemon=True)
        self.worker_thread.start()

        logger.info("✅ Merge Coordinator initialized")

    def queue_merge(self, task_id: str, pr_url: str, branch_name: str, agent_id: str):
        """
        Add PR to merge queue

        Returns: Queue position
        """
        merge_request = {
            "task_id": task_id,
            "pr_url": pr_url,
            "branch_name": branch_name,
            "agent_id": agent_id,
            "queued_at": datetime.now().isoformat(),
            "status": "queued",
            "retry_count": 0
        }

        # Add to queue
        self.redis.rpush(self.merge_queue_key, json.dumps(merge_request))

        queue_length = self.redis.llen(self.merge_queue_key)

        logger.info(f"📝 Merge queued: {task_id} (PR: {pr_url}, Queue: {queue_length})")

        return queue_length

    def _merge_worker(self):
        """
        Background worker that processes merge queue sequentially
        """
        logger.info("🔄 Merge worker started")

        while self.running:
            try:
                # Get next merge request from queue (blocking, timeout 5s)
                result = self.redis.blpop(self.merge_queue_key, timeout=5)

                if not result:
                    continue

                _, merge_request_json = result
                merge_request = json.loads(merge_request_json)

                # Process merge
                self._process_merge(merge_request)

            except Exception as e:
                logger.error(f"❌ Merge worker error: {e}")
                time.sleep(5)

    def _process_merge(self, merge_request: dict):
        """
        Process a single merge request

        Workflow:
        1. Update main branch
        2. Check for conflicts
        3. Run tests
        4. Merge PR
        5. Cleanup branch
        6. Notify agent
        """
        task_id = merge_request['task_id']
        branch_name = merge_request['branch_name']
        pr_url = merge_request['pr_url']
        agent_id = merge_request['agent_id']
        retry_count = merge_request.get('retry_count', 0)

        logger.info(f"🔀 Processing merge: {task_id} (branch: {branch_name})")

        # Mark as active
        self.redis.hset(self.active_merges_key, task_id, json.dumps(merge_request))

        try:
            # Step 1: Update main branch
            logger.info(f"   [1/6] Updating main branch...")
            self._update_main_branch()

            # Step 2: Check for conflicts
            logger.info(f"   [2/6] Checking for conflicts...")
            has_conflict = self._check_conflicts(branch_name)

            if has_conflict:
                logger.warning(f"   ⚠️  Conflict detected in {branch_name}")
                self._handle_conflict(merge_request)
                return

            # Step 3: Run tests
            if self.config['quality_gates']['run_tests']:
                logger.info(f"   [3/6] Running tests...")
                tests_passed = self._run_tests(branch_name)

                if not tests_passed:
                    logger.warning(f"   ❌ Tests failed for {branch_name}")
                    self._handle_test_failure(merge_request)
                    return
            else:
                logger.info(f"   [3/6] Tests skipped (disabled in config)")

            # Step 4: Merge PR
            logger.info(f"   [4/6] Merging PR...")
            merge_success = self._merge_pr(pr_url, branch_name)

            if not merge_success:
                logger.error(f"   ❌ Merge failed for {task_id}")
                self._handle_merge_failure(merge_request)
                return

            # Step 5: Cleanup branch
            logger.info(f"   [5/6] Cleaning up branch...")
            self._cleanup_branch(branch_name)

            # Step 6: Update task status
            logger.info(f"   [6/6] Updating task status...")
            self._mark_task_merged(task_id)

            logger.info(f"✅ Merge complete: {task_id}")

            # Notify agent
            self._notify_agent(agent_id, task_id, "merge_success", {
                "message": f"Task {task_id} successfully merged to main"
            })

            # Check if phase can advance
            self._check_phase_advancement()

        except Exception as e:
            logger.error(f"❌ Merge error for {task_id}: {e}")
            self._handle_merge_failure(merge_request)

        finally:
            # Remove from active merges
            self.redis.hdel(self.active_merges_key, task_id)

    def _update_main_branch(self):
        """Update local main branch from remote"""
        try:
            # Ensure we're on main
            subprocess.run(
                ["git", "checkout", self.config['git']['main_branch']],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )

            # Pull latest changes (if remote exists)
            if self.config['git'].get('push_to_remote', True):
                try:
                    subprocess.run(
                        ["git", "pull", "--rebase"],
                        cwd=self.project_root,
                        check=True,
                        capture_output=True
                    )
                except subprocess.CalledProcessError:
                    logger.warning("Could not pull from remote (might not exist)")

        except Exception as e:
            logger.error(f"Failed to update main: {e}")
            raise

    def _check_conflicts(self, branch_name: str) -> bool:
        """
        Check if branch has conflicts with main

        Returns: True if conflicts exist, False otherwise
        """
        try:
            # Try to merge branch into main (dry run)
            result = subprocess.run(
                ["git", "merge", "--no-commit", "--no-ff", branch_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            # Abort the merge (Fix #9: ignore errors if no merge to abort)
            subprocess.run(
                ["git", "merge", "--abort"],
                cwd=self.project_root,
                capture_output=True,
                check=False  # Don't raise on error (might not be a merge in progress)
            )

            # Check for conflict indicators
            if result.returncode != 0:
                if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                    return True

            return False

        except Exception as e:
            logger.error(f"Conflict check failed: {e}")
            return True  # Assume conflict on error

    def _run_tests(self, branch_name: str) -> bool:
        """
        Run tests on branch

        Returns: True if tests pass, False otherwise
        """
        try:
            # Checkout branch
            subprocess.run(
                ["git", "checkout", branch_name],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )

            # Run quality checks
            checks = self.config['quality_gates']['checks']

            for check in checks:
                if not check.get('required', False):
                    continue

                logger.info(f"      Running: {check['name']}...")

                try:
                    subprocess.run(
                        check['command'].split(),
                        cwd=self.project_root,
                        check=True,
                        capture_output=True,
                        timeout=300  # 5 min timeout
                    )
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    logger.warning(f"      ❌ {check['name']} failed")
                    return False

            # Go back to main
            subprocess.run(
                ["git", "checkout", self.config['git']['main_branch']],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )

            return True

        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return False

    def _merge_pr(self, pr_url: str, branch_name: str) -> bool:
        """
        Merge PR using GitHub CLI or git merge

        Returns: True if successful, False otherwise
        """
        try:
            # If push_to_remote enabled, use gh CLI
            if self.config['git'].get('push_to_remote', True):
                # Check if PR URL exists (Fix #5: local mode pr_url can be None)
                if not pr_url:
                    logger.warning(f"No PR URL provided (local mode?), using local merge")
                    # Fall through to local merge
                else:
                    # Extract PR number from URL
                    pr_number = pr_url.split('/')[-1]

                    # Merge using gh CLI
                    result = subprocess.run(
                        ["gh", "pr", "merge", pr_number, "--squash", "--delete-branch"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True
                    )

                    return result.returncode == 0

            # Local merge (no remote or no PR URL)
            if not self.config['git'].get('push_to_remote', True) or not pr_url:
                # Local merge (no remote)
                # Merge branch to main
                subprocess.run(
                    ["git", "merge", "--squash", branch_name],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )

                # Commit
                subprocess.run(
                    ["git", "commit", "-m", f"Merge {branch_name}"],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True
                )

                return True

        except Exception as e:
            logger.error(f"PR merge failed: {e}")
            return False

    def _cleanup_branch(self, branch_name: str):
        """Delete merged branch"""
        try:
            # Delete local branch
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                cwd=self.project_root,
                capture_output=True
            )

            # Delete remote branch (if exists)
            if self.config['git'].get('push_to_remote', True):
                subprocess.run(
                    ["git", "push", "origin", "--delete", branch_name],
                    cwd=self.project_root,
                    capture_output=True
                )

        except Exception as e:
            logger.warning(f"Branch cleanup failed: {e}")

    def _mark_task_merged(self, task_id: str):
        """Mark task as merged in Redis"""
        task_json = self.redis.hget("orchestrator:tasks", task_id)
        if task_json:
            task = json.loads(task_json)
            task['status'] = 'merged'
            task['merged_at'] = datetime.now().isoformat()
            self.redis.hset("orchestrator:tasks", task_id, json.dumps(task))

    def _handle_conflict(self, merge_request: dict):
        """
        Handle merge conflict

        Strategy:
        1. Notify agent
        2. Agent fixes conflict
        3. Retry merge
        """
        task_id = merge_request['task_id']
        agent_id = merge_request['agent_id']
        branch_name = merge_request['branch_name']

        logger.warning(f"🔧 Handling conflict for {task_id}")

        # Mark task as needs_conflict_resolution
        task_json = self.redis.hget("orchestrator:tasks", task_id)
        if task_json:
            task = json.loads(task_json)
            task['status'] = 'conflict'
            task['conflict_info'] = {
                "branch": branch_name,
                "detected_at": datetime.now().isoformat()
            }
            self.redis.hset("orchestrator:tasks", task_id, json.dumps(task))

        # Notify agent to fix conflict
        self._notify_agent(agent_id, task_id, "conflict_detected", {
            "message": f"Merge conflict detected in {branch_name}",
            "branch": branch_name,
            "action_required": "resolve_conflict"
        })

        # Add to retry queue (after agent fixes)
        # Agent will re-push and trigger new merge

    def _handle_test_failure(self, merge_request: dict):
        """
        Handle test failure

        Strategy:
        1. Notify agent
        2. Agent fixes tests
        3. Retry merge
        """
        task_id = merge_request['task_id']
        agent_id = merge_request['agent_id']

        logger.warning(f"🧪 Handling test failure for {task_id}")

        # Mark task as test_failed
        task_json = self.redis.hget("orchestrator:tasks", task_id)
        if task_json:
            task = json.loads(task_json)
            task['status'] = 'test_failed'
            self.redis.hset("orchestrator:tasks", task_id, json.dumps(task))

        # Notify agent
        self._notify_agent(agent_id, task_id, "tests_failed", {
            "message": f"Tests failed for {task_id}",
            "action_required": "fix_tests"
        })

    def _handle_merge_failure(self, merge_request: dict):
        """
        Handle general merge failure

        Strategy:
        1. Retry up to 3 times
        2. If still fails, notify agent
        """
        task_id = merge_request['task_id']
        retry_count = merge_request.get('retry_count', 0)

        logger.warning(f"⚠️  Merge failure for {task_id} (retry {retry_count}/3)")

        if retry_count < 3:
            # Retry
            merge_request['retry_count'] = retry_count + 1
            time.sleep(5 * (retry_count + 1))  # Exponential backoff

            # Re-queue
            self.redis.rpush(self.merge_queue_key, json.dumps(merge_request))
            logger.info(f"🔄 Re-queued {task_id} for retry")

        else:
            # Max retries exceeded
            logger.error(f"❌ Max retries exceeded for {task_id}")

            # Mark as failed
            task_json = self.redis.hget("orchestrator:tasks", task_id)
            if task_json:
                task = json.loads(task_json)
                task['status'] = 'merge_failed'
                self.redis.hset("orchestrator:tasks", task_id, json.dumps(task))

            # Notify agent
            self._notify_agent(merge_request['agent_id'], task_id, "merge_failed", {
                "message": f"Merge failed after 3 retries for {task_id}",
                "action_required": "manual_intervention"
            })

    def _notify_agent(self, agent_id: str, task_id: str, event_type: str, data: dict):
        """
        Notify agent about merge event

        Uses Redis pub/sub for real-time notifications
        """
        notification = {
            "agent_id": agent_id,
            "task_id": task_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        # Publish to agent's notification channel
        channel = f"agent:{agent_id}:notifications"
        self.redis.publish(channel, json.dumps(notification))

        # Also store in Redis for later retrieval
        notif_key = f"agent:{agent_id}:notifications:pending"
        self.redis.rpush(notif_key, json.dumps(notification))

        logger.info(f"📬 Notified {agent_id}: {event_type} for {task_id}")

    def _check_phase_advancement(self):
        """
        Check if current phase is complete and can advance

        Called after each successful merge

        Fix #17: Phase can advance even if some tasks are 'blocked'
        """
        try:
            # Get current phase
            phase_json = self.redis.get("orchestrator:current_phase")
            if not phase_json:
                return

            phase = json.loads(phase_json)

            # Check if all tasks in phase are in terminal state
            # Terminal states: merged, failed, blocked
            all_complete = True
            for task_id in phase['tasks']:
                task_json = self.redis.hget("orchestrator:tasks", task_id)
                if not task_json:
                    continue

                task = json.loads(task_json)
                status = task['status']

                # Fix #17: Include 'blocked' as terminal state
                if status not in ['merged', 'failed', 'blocked']:
                    all_complete = False
                    break

            if all_complete:
                logger.info(f"✅ Phase {phase['id']} ({phase['name']}) complete!")

                # Mark phase as complete
                phase['status'] = 'completed'
                phase['completed_at'] = datetime.now().isoformat()

                # Move to next phase
                phases_json = self.redis.get("orchestrator:phases")
                if phases_json:
                    phases = json.loads(phases_json)

                    # Find next phase
                    next_phase_idx = phase['id']
                    if next_phase_idx < len(phases):
                        next_phase = phases[next_phase_idx]
                        next_phase['status'] = 'active'
                        next_phase['started_at'] = datetime.now().isoformat()

                        # Save updated phases
                        phases[phase['id'] - 1] = phase
                        phases[next_phase_idx] = next_phase
                        self.redis.set("orchestrator:phases", json.dumps(phases))

                        # Set as current phase
                        self.redis.set("orchestrator:current_phase", json.dumps(next_phase))

                        logger.info(f"📍 Starting Phase {next_phase['id']} ({next_phase['name']})")
                    else:
                        logger.info("🎉 All phases complete!")
                        self.redis.delete("orchestrator:current_phase")

        except Exception as e:
            logger.error(f"Error checking phase advancement: {e}")

    def stop(self):
        """Stop merge coordinator"""
        logger.info("🛑 Stopping merge coordinator...")
        self.running = False
        self.worker_thread.join(timeout=10)
