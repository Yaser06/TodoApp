---
language: "TypeScript"
version: "5.0+"
framework: "NestJS"
frameworkVersion: "10.0+"
packageManager: "npm / pnpm / yarn"
keyLibraries:
  - "@nestjs/typeorm (database ORM)"
  - "@nestjs/passport (authentication)"
  - "@nestjs/swagger (API docs)"
  - "class-validator (validation)"
  - "class-transformer (serialization)"
architecture: "Modular with Dependency Injection"
testFramework: "Jest (unit) + Supertest (e2e)"
buildTool: "TypeScript compiler / Webpack"
linting: "ESLint + Prettier"
---

# Tech Profile — NestJS

## Core Stack

**Language**: TypeScript 5.0+
**Framework**: NestJS 10+
**HTTP**: Express (default) or Fastify
**ORM**: TypeORM, Prisma, or Mongoose
**Validation**: class-validator
**Auth**: Passport.js strategies
**Docs**: Swagger/OpenAPI

## Project Structure

```
src/
├── main.ts                  # Bootstrap
├── app.module.ts            # Root module
├── common/                  # Shared code
│   ├── decorators/
│   ├── guards/
│   ├── interceptors/
│   └── filters/
├── config/                  # Configuration
│   └── configuration.ts
├── users/                   # Feature module
│   ├── users.module.ts
│   ├── users.controller.ts
│   ├── users.service.ts
│   ├── entities/user.entity.ts
│   ├── dto/
│   │   ├── create-user.dto.ts
│   │   └── update-user.dto.ts
│   └── users.controller.spec.ts
└── auth/                    # Auth module
```

## Module Pattern

```typescript
@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],  // For other modules
})
export class UsersModule {}
```

## Dependency Injection

```typescript
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
    private configService: ConfigService,
  ) {}

  async findOne(id: number): Promise<User> {
    return this.usersRepository.findOne({ where: { id } })
  }
}
```

## DTOs & Validation

```typescript
import { IsEmail, IsString, MinLength } from 'class-validator'

export class CreateUserDto {
  @IsEmail()
  email: string

  @IsString()
  @MinLength(8)
  password: string
}

// Controller
@Post()
async create(@Body() createUserDto: CreateUserDto) {
  return this.usersService.create(createUserDto)
}
```

## Guards & Auth

```typescript
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

@Controller('users')
@UseGuards(JwtAuthGuard)
export class UsersController {
  @Get('profile')
  getProfile(@Request() req) {
    return req.user
  }
}
```

## Exception Filters

```typescript
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp()
    const response = ctx.getResponse()
    const status = exception.getStatus()

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      message: exception.message,
    })
  }
}
```

## Configuration

```typescript
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule)

  app.useGlobalPipes(new ValidationPipe())
  app.useGlobalFilters(new HttpExceptionFilter())

  const config = new DocumentBuilder()
    .setTitle('API')
    .setVersion('1.0')
    .addBearerAuth()
    .build()
  const document = SwaggerModule.createDocument(app, config)
  SwaggerModule.setup('api/docs', app, document)

  await app.listen(3000)
}
bootstrap()
```
