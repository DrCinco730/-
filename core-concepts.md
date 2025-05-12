# Core Concepts

This document explains the fundamental concepts of Neo4j-ORM.

## Entity

An Entity is a class that maps to a Neo4j node. Each entity class corresponds to a node label in the database.

```typescript
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property()
  name: string;

  @Property({ unique: true })
  email: string;
}
```

In this example:
- The `@Entity()` decorator marks the class as an entity
- The `User` class maps to nodes with the label `User` in the database
- Each property marked with a decorator corresponds to a property on the node

### Entity Options

You can customize the entity behavior:

```typescript
@Entity({
  name: 'Person', // Use 'Person' label in the database instead of 'User'
  synchronize: true // Allow automatic schema synchronization
})
class User {
  // ...
}
```

## DataSource

The DataSource is the main entry point for connecting to a Neo4j database:

```typescript
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User, Post, Comment],
  synchronize: true,
  logging: true
});

// Initialize the connection
await dataSource.initialize();
```

The DataSource is responsible for:
- Establishing and managing database connections
- Providing access to entity repositories
- Managing transactions
- Running migrations
- Creating constraints and indices (when `synchronize` is true)

## Repository

Repositories provide methods to interact with entities in the database:

```typescript
// Get a repository for the User entity
const userRepository = dataSource.getRepository(User);

// Create a new user
const user = userRepository.create({ name: 'John', email: 'john@example.com' });

// Save the user to the database
await userRepository.save(user);

// Find all users
const allUsers = await userRepository.find();

// Find one user by criteria
const john = await userRepository.findOne({ where: { email: 'john@example.com' } });

// Update a user
if (john) {
  john.name = 'John Smith';
  await userRepository.save(john);
}

// Delete a user
if (john) {
  await userRepository.remove(john);
}
```

Key repository methods:
- `create(data)`: Create a new entity instance (not saved to the database yet)
- `save(entity)`: Save an entity to the database (creates if new, updates if existing)
- `find(options)`: Find entities that match the given criteria
- `findOne(options)`: Find one entity that matches the given criteria
- `findOneById(id)`: Find an entity by its ID
- `update(id, partialEntity)`: Update an entity by ID
- `remove(entity)`: Remove an entity from the database
- `softRemove(entity)`: Soft delete an entity (using a delete date column)
- `recover(entity)`: Recover a soft-deleted entity
- `count(options)`: Count entities that match the given criteria

## QueryBuilder

QueryBuilder provides a fluent API for building complex Cypher queries:

```typescript
const queryBuilder = dataSource.createQueryBuilder();

queryBuilder
  .match('u', User)
  .where('u.age > 18')
  .return('u')
  .orderBy('u.name', 'ASC')
  .limit(10);

const users = await queryBuilder.getMany();
```

QueryBuilder is useful for:
- Complex queries beyond the capabilities of the repository methods
- Queries involving multiple entities and relationships
- Custom projections and aggregations
- Performance-critical operations

## EntityManager

The EntityManager provides a higher-level API for working with entities:

```typescript
const entityManager = dataSource.createEntityManager();

// Find users
const users = await entityManager.find(User, { where: { active: true } });

// Create and save in one step
const post = await entityManager.save(Post, {
  title: 'Hello World',
  content: 'This is my first post',
  author: users[0]
});
```

It also supports transactions:

```typescript
const result = await entityManager.transaction(async transactionManager => {
  const user = transactionManager.create(User, { name: 'Alice' });
  await transactionManager.save(user);
  return user;
});
```

## Relationships

Relationships between entities are defined using the `@Relationship` decorator:

```typescript
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property()
  name: string;

  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: Post,
    cascade: true
  })
  posts: Post[];
}

@Entity()
class Post {
  @NodeId({ generated: true })
  id: string;

  @Property()
  title: string;

  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: User
  })
  author: User;
}
```

The `@Relationship` decorator configures:
- `type`: The name of the relationship in Neo4j
- `direction`: The direction of the relationship (`IN`, `OUT`, or `NONE`)
- `target`: The target entity class
- `cascade`: Whether to automatically save related entities
- `eager`: Whether to automatically load the relationship
- `lazy`: Whether to load the relationship only when accessed

## Transactions

Transactions ensure that a series of operations succeed or fail as a unit:

```typescript
await dataSource.transaction(async manager => {
  const user = manager.create(User, { name: 'Bob' });
  await manager.save(user);

  const post = manager.create(Post, { title: 'My Post', author: user });
  await manager.save(post);

  // If any operation fails, the entire transaction is rolled back
});
```

## Events and Subscribers

Entity lifecycle events allow you to execute code at specific points:

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  email: string;

  @BeforeInsert()
  normalizeEmail() {
    this.email = this.email.toLowerCase().trim();
  }
}
```

Event subscribers provide a more centralized approach:

```typescript
@EventSubscriber()
class UserSubscriber implements EntitySubscriberInterface<User> {
  listenTo() {
    return User;
  }

  async beforeInsert(event: InsertEvent<User>) {
    console.log('About to insert a user:', event.entity);
  }

  async afterInsert(event: InsertEvent<User>) {
    // Send welcome email
    const emailService = new EmailService();
    await emailService.sendWelcomeEmail(event.entity.email);
  }
}
```

## Migrations

Migrations help you manage database schema changes over time:

```typescript
export class AddUserVerification20230101 implements MigrationInterface {
  async up(queryRunner: AdaptedQueryRunner): Promise<any> {
    await queryRunner.query(`
      MATCH (u:User)
      WHERE NOT EXISTS(u.isVerified)
      SET u.isVerified = false
    `);
  }

  async down(queryRunner: AdaptedQueryRunner): Promise<any> {
    await queryRunner.query(`
      MATCH (u:User)
      WHERE EXISTS(u.isVerified)
      REMOVE u.isVerified
    `);
  }
}
```

Running migrations:

```typescript
// Run all pending migrations
await dataSource.runMigrations();
```

These core concepts form the foundation of Neo4j-ORM. Understanding them will help you build effective graph database applications.
