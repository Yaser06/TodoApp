---
architectureStyle: "Modular + Dependency Injection"
layering: "Controller → Service → Repository"
errorStrategy: "Exception filters + HTTP exceptions"
testingApproach: "Jest with mocking"
observability: "Winston logger + custom interceptors"
---

# Pattern Profile — NestJS

## Layered Architecture

```
Controller → Service → Repository → Database
  ↓            ↓           ↓
 HTTP       Business    Data Access
```

## Repository Pattern

```typescript
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepo: Repository<User>,
  ) {}

  async findAll(): Promise<User[]> {
    return this.usersRepo.find()
  }

  async create(dto: CreateUserDto): Promise<User> {
    const user = this.usersRepo.create(dto)
    return this.usersRepo.save(user)
  }
}
```

## Interceptor Pattern

```typescript
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const now = Date.now()
    return next
      .handle()
      .pipe(
        tap(() => console.log(`After... ${Date.now() - now}ms`)),
      )
  }
}
```

## Testing Pattern

```typescript
describe('UsersService', () => {
  let service: UsersService
  let repo: Repository<User>

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: getRepositoryToken(User),
          useValue: {
            find: jest.fn(),
            findOne: jest.fn(),
          },
        },
      ],
    }).compile()

    service = module.get<UsersService>(UsersService)
    repo = module.get<Repository<User>>(getRepositoryToken(User))
  })

  it('should find all users', async () => {
    jest.spyOn(repo, 'find').mockResolvedValue([])
    expect(await service.findAll()).toEqual([])
  })
})
```
