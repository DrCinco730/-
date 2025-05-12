# Neo4j-ORM Documentation

Neo4j-ORM is a robust Object-Relational Mapping (ORM) library for Neo4j graph databases in TypeScript/JavaScript applications. It provides a familiar TypeORM-like API for working with Neo4j, making it easier for developers to interact with graph databases using an object-oriented approach.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
  - [DataSource](#datasource)
  - [Entities](#entities)
  - [Repositories](#repositories)
  - [Relationships](#relationships)
  - [Queries](#queries)
- [Decorators](#decorators)
  - [Entity Decorators](#entity-decorators)
  - [Property Decorators](#property-decorators)
  - [Relationship Decorators](#relationship-decorators)
  - [Event Decorators](#event-decorators)
- [Querying](#querying)
  - [Repository API](#repository-api)
  - [QueryBuilder](#querybuilder)
  - [Custom Queries](#custom-queries)
- [Transactions](#transactions)
- [Events and Subscribers](#events-and-subscribers)
- [Migrations](#migrations)
- [Error Handling](#error-handling)
- [Utilities](#utilities)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)

## Installation

```bash
npm install neo4j-orm neo4j-driver reflect-metadata
```

Or using yarn:

```bash
yarn add neo4j-orm neo4j-driver reflect-metadata
```

Make sure to import `reflect-metadata` at the entry point of your application:

```typescript
import 'reflect-metadata';
```

## Getting Started

### Basic Setup

```typescript
import { DataSource, Entity, NodeId, Property } from 'neo4j-orm';

// Define an entity
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property()
  email: string;
}

// Create a data source
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User]
});

// Initialize connection
async function main() {
  await dataSource.initialize();

  // Get repository
  const userRepository = dataSource.getRepository(User);

  // Create a new user
  const user = userRepository.create({
    name: 'John Doe',
    email: 'john@example.com'
  });

  // Save user
  await userRepository.save(user);

  // Find users
  const users = await userRepository.find();
  console.log(users);

  // Close connection
  await dataSource.destroy();
}

main().catch(console.error);
```

## Core Concepts

### DataSource

The DataSource is the main entry point for connecting to a Neo4j database. It's responsible for:

- Establishing and maintaining database connections
- Managing entity repositories
- Handling transactions
- Executing migrations

```typescript
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User, Post, Comment],
  synchronize: true, // Automatically create constraints and indices
  logging: true      // Enable query logging
});

// Initialize the connection
await dataSource.initialize();
```

### Entities

Entities are classes that map to Neo4j nodes. Each entity class corresponds to a node label in Neo4j.

```typescript
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false, unique: true })
  email: string;

  @Property()
  firstName: string;

  @Property()
  lastName: string;

  @Property({ type: 'number' })
  age: number;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

### Repositories

Repositories provide methods to interact with entities in the database:

```typescript
// Get repository for User entity
const userRepository = dataSource.getRepository(User);

// Create a new user
const user = userRepository.create({
  email: 'jane@example.com',
  firstName: 'Jane',
  lastName: 'Smith',
  age: 30
});

// Save user to database
await userRepository.save(user);

// Find all users
const allUsers = await userRepository.find();

// Find users with specific criteria
const adultUsers = await userRepository.find({
  where: { age: { [Op.gte]: 18 } }
});

// Find one user
const jane = await userRepository.findOne({
  where: { email: 'jane@example.com' }
});

// Update user
await userRepository.update(jane.id, { age: 31 });

// Delete user
await userRepository.remove(jane);
```

### Relationships

Neo4j-ORM provides decorators for defining relationships between entities:

```typescript
@Entity()
class Post {
  @NodeId({ generated: true })
  id: string;

  @Property()
  title: string;

  @Property()
  content: string;

  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: User
  })
  author: User;

  @Relationship({
    type: 'HAS_COMMENT',
    direction: 'OUT', 
    target: Comment,
    cascade: true
  })
  comments: Comment[];
}

@Entity()
class Comment {
  @NodeId({ generated: true })
  id: string;

  @Property()
  text: string;

  @Relationship({
    type: 'COMMENTED_BY',
    direction: 'OUT',
    target: User
  })
  author: User;

  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT', 
    target: Post
  })
  post: Post;
}
```

### Queries

Neo4j-ORM provides a QueryBuilder API for constructing complex Cypher queries:

```typescript
const queryBuilder = dataSource.createQueryBuilder();

queryBuilder
  .match({ identifier: 'u', label: 'User' })
  .where('u.age > $minAge')
  .with('u')
  .match({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'AUTHORED' },
      { identifier: 'p', label: 'Post' }
    ]
  })
  .return('u, count(p) as postCount')
  .orderBy('postCount', 'DESC')
  .limit(10);

const result = await queryBuilder.getRaw();
```

## Decorators

### Entity Decorators

- `@Entity(options?: EntityOptions)`: Marks a class as an entity (Neo4j node)
  - `options.name`: Custom label name (defaults to class name)
  - `options.synchronize`: Whether to create constraints/indices on startup

- `@Unique(propertyNames: string[])`: Creates a composite unique constraint

- `@Index(name?: string, options?: { unique?: boolean, columns?: string[] })`: Creates an index

### Property Decorators

- `@Property(options?: PropertyOptions)`: Marks a property to be stored in the database
  - `options.type`: Property type ('string', 'number', 'boolean', 'date', etc.)
  - `options.nullable`: Whether the property can be null
  - `options.default`: Default value
  - `options.index`: Whether to create an index
  - `options.unique`: Whether to create a unique constraint

- `@NodeId(options?: NodeIdOptions)`: Marks a property as the primary identifier
  - `options.generated`: Auto-generate UUID if not provided
  - `options.type`: Property type (defaults to 'string')
  - `options.primary`: Whether this is the primary key (always true)

- `@CreateDateColumn()`: Automatically sets the property to the creation date

- `@UpdateDateColumn()`: Automatically updates to current date on entity update

- `@VersionColumn()`: Increments version on each update

- `@DeleteDateColumn()`: Sets to current date when entity is soft-deleted

### Relationship Decorators

- `@Relationship(options: RelationshipOptions)`: Defines a relationship to another entity
  - `options.type`: Relationship type name in Neo4j
  - `options.direction`: 'IN', 'OUT', or 'NONE'
  - `options.target`: Target entity class
  - `options.cascade`: Whether to cascade operations (true/false/string[])
  - `options.eager`: Whether to always load the relationship
  - `options.lazy`: Whether to load the relationship only when accessed

- `@RelationshipProperty(options?: RelationshipPropertyOptions)`: Defines a property on a relationship

- `@RelationshipProperties()`: Marks an object that contains relationship properties

### Event Decorators

- `@BeforeInsert()`: Method runs before entity insert
- `@AfterInsert()`: Method runs after entity insert
- `@BeforeUpdate()`: Method runs before entity update
- `@AfterUpdate()`: Method runs after entity update
- `@BeforeRemove()`: Method runs before entity removal
- `@AfterRemove()`: Method runs after entity removal
- `@BeforeSoftRemove()`: Method runs before entity soft removal
- `@AfterSoftRemove()`: Method runs after entity soft removal
- `@BeforeRecover()`: Method runs before recovering a soft-deleted entity
- `@AfterRecover()`: Method runs after recovering a soft-deleted entity

- `@EventSubscriber()`: Marks a class as an event subscriber

## Querying

### Repository API

Repositories provide several methods for working with entities:

- `find(options?: FindOptions<Entity>)`: Find entities that match given conditions
- `findOne(options?: FindOneOptions<Entity>)`: Find one entity that matches given conditions
- `findOneById(id: string | number | Record<string, any>)`: Find an entity by its ID
- `create(entityLike: Partial<Entity>)`: Create a new entity instance
- `save(entities: Entity | Entity[], options?: SaveOptions)`: Save one or more entities
- `update(id: string | number | Record<string, any>, partialEntity: Partial<Entity>)`: Update an entity
- `softRemove(entities: Entity | Entity[])`: Soft-delete one or more entities
- `recover(entities: Entity | Entity[])`: Recover soft-deleted entities
- `count(options?: FindOptions<Entity>)`: Count entities matching given criteria
- `upsert(entityLike: Partial<Entity>, uniqueBy: (keyof Entity)[])`: Create or update an entity

```typescript
// Find options
const options = {
  where: { age: { [Op.gte]: 18 } },        // Where conditions
  relations: ['posts', 'posts.comments'],  // Relationships to load
  skip: 0,                                 // Skip N records
  take: 10,                                // Take N records
  order: [['createdAt', 'DESC']]           // Order by property
};

const users = await userRepository.find(options);
```

### QueryBuilder

The QueryBuilder API provides a fluent interface for creating Cypher queries:

```typescript
const queryBuilder = userRepository.createQueryBuilder();

queryBuilder
  .match('user', User)
  .where('user.age > 21')
  .return('user')
  .orderBy('user.name', 'ASC')
  .skip(10)
  .limit(10);

const users = await queryBuilder.getMany();
```

Methods:
- `match(nodeOrAlias: string | any, entityClass?: new (...args: any[]) => any)`
- `leftJoin(property: string, alias: string)`
- `leftJoinAndSelect(property: string, alias: string)`
- `innerJoin(property: string, alias: string, condition?: string)`
- `innerJoinAndSelect(property: string, alias: string, condition?: string)`
- `where(condition: string | Function, parameters?: any)`
- `andWhere(condition: string | Function, parameters?: any)`
- `orWhere(condition: string | Function, parameters?: any)`
- `orderBy(sort: string, order: 'ASC' | 'DESC' = 'ASC')`
- `skip(count: number)`
- `limit(count: number)`
- `return(value: string)`
- `create(options: any)`
- `set(options: any)`
- `delete(options: any)`
- `with(expression: string)`

Execution methods:
- `getRaw(): Promise<any>`
- `getRawOne(): Promise<any>`
- `getRawMany(): Promise<any[]>`
- `getCount(): Promise<number>`
- `getManyAndCount(): Promise<[any[], number]>`
- `getMany<T = any>(): Promise<T[]>`
- `getOne<T = any>(): Promise<T | null>`
- `execute(): Promise<void>`

### Custom Queries

Execute custom Cypher queries:

```typescript
// Using DataSource
const result = await dataSource.query(
  'MATCH (u:User)-[:AUTHORED]->(p:Post) WHERE u.name = $name RETURN u, p',
  { name: 'John Doe' }
);

// Using EntityManager
const entityManager = dataSource.createEntityManager();
const result = await entityManager.query(
  'MATCH (u:User) WHERE u.email = $email RETURN u',
  { email: 'john@example.com' }
);
```

## Transactions

Neo4j-ORM provides transaction support:

```typescript
// Using DataSource
const result = await dataSource.transaction(async manager => {
  // Get repositories
  const userRepo = manager.getRepository(User);
  const postRepo = manager.getRepository(Post);

  // Create user
  const user = userRepo.create({ name: 'Jane', email: 'jane@example.com' });
  await userRepo.save(user);

  // Create post
  const post = postRepo.create({ title: 'My Post', content: 'Hello world!', author: user });
  await postRepo.save(post);

  return { user, post };
});

// Using EntityManager
const entityManager = dataSource.createEntityManager();

const result = await entityManager.transaction(async transactionManager => {
  // Operations in transaction
  const user = transactionManager.getRepository(User).create({ name: 'Alice' });
  await transactionManager.getRepository(User).save(user);
  return user;
});
```

## Events and Subscribers

### Entity Listeners

```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @Property({ default: false })
  isVerified: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @BeforeInsert()
  beforeInsert() {
    console.log('About to insert a new user:', this.name);
  }

  @AfterInsert()
  afterInsert() {
    console.log('User inserted successfully:', this.id);
  }

  @BeforeUpdate()
  beforeUpdate() {
    console.log('About to update user:', this.id);
  }
}
```

### Entity Subscribers

```typescript
@EventSubscriber()
class UserSubscriber implements EntitySubscriberInterface<User> {
  listenTo() {
    return User;
  }

  async beforeInsert(event: InsertEvent<User>) {
    console.log('BEFORE USER INSERTED:', event.entity);
  }

  async afterInsert(event: InsertEvent<User>) {
    console.log('AFTER USER INSERTED:', event.entity);
    
    // Perform additional operations
    const emailService = new EmailService();
    await emailService.sendWelcomeEmail(event.entity.email);
  }

  async beforeUpdate(event: UpdateEvent<User>) {
    console.log('BEFORE USER UPDATED:', event.entity);
  }
}

// Register subscribers
dataSource.registerSubscribers();
```

## Migrations

Neo4j-ORM provides a framework for database migrations:

```typescript
// migration-20230101.ts
import { MigrationInterface, AdaptedQueryRunner } from 'neo4j-orm';

export class AddEmailVerification20230101 implements MigrationInterface {
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
// In your application
const migrations = await dataSource.runMigrations();
console.log('Migrations applied:', migrations);
```

## Error Handling

Neo4j-ORM provides custom error classes:

```typescript
try {
  await userRepository.save(user);
} catch (error) {
  if (error instanceof Neo4jORMError) {
    console.error('ORM Error:', error.message);
  }
  
  if (error instanceof ConnectionError) {
    console.error('Connection Error:', error.message);
  }
  
  if (error instanceof QueryError) {
    console.error('Query Error:', error.message);
    console.error('Query:', error.query);
    console.error('Parameters:', error.params);
  }
  
  if (error instanceof EntityNotFoundError) {
    console.error('Entity Not Found:', error.message);
  }
  
  if (error instanceof MetadataError) {
    console.error('Metadata Error:', error.message);
  }
  
  if (error instanceof CompositeUniqueError) {
    console.error('Composite Unique Constraint Violation:', error.message);
  }
}
```

## Utilities

Neo4j-ORM includes utility functions:

```typescript
import { Neo4jOrmUtils, Logger, LogLevel } from 'neo4j-orm';

// Set logger level
Logger.instance.setLevel(LogLevel.DEBUG);

// Generate UUID
const uuid = Neo4jOrmUtils.generateUuid();

// Check if object is empty
const isEmpty = Neo4jOrmUtils.isEmptyObject(obj);

// Format strings
const humanReadable = Neo4jOrmUtils.camelToHuman('firstName'); // "First Name"
const snakeCase = Neo4jOrmUtils.camelToSnake('firstName');     // "first_name"

// Sanitize inputs
const safeName = Neo4jOrmUtils.sanitizeIdentifier(userInput);
const safeLabel = Neo4jOrmUtils.sanitizeLabel(userInput);
const safeCondition = Neo4jOrmUtils.sanitizeCondition(userInput);
const safeParams = Neo4jOrmUtils.sanitizeParameters(userInput);
```

## Advanced Features

### Operators for Queries

Neo4j-ORM provides operators for advanced querying:

```typescript
import { Op } from 'neo4j-orm';

const users = await userRepository.find({
  where: {
    age: { [Op.gt]: 18 },
    name: { [Op.contains]: 'John' },
    status: { [Op.in]: ['active', 'pending'] },
    lastLogin: { [Op.lte]: new Date() }
  }
});
```

Available operators:
- `Op.eq`: Equals
- `Op.ne`: Not equals
- `Op.gt`: Greater than
- `Op.gte`: Greater than or equal
- `Op.lt`: Less than
- `Op.lte`: Less than or equal
- `Op.in`: In array
- `Op.notIn`: Not in array
- `Op.like`: Like pattern
- `Op.notLike`: Not like pattern
- `Op.contains`: Contains substring
- `Op.startsWith`: Starts with substring
- `Op.endsWith`: Ends with substring
- `Op.between`: Between two values

### Update Operators

For partial updates:

```typescript
import { UpdateOp } from 'neo4j-orm';

await userRepository.update(userId, {
  loginCount: { [UpdateOp.inc]: 1 },         // Increment by 1
  lastLogin: { [UpdateOp.set]: new Date() }, // Set to value
  oldEmails: { [UpdateOp.push]: email }      // Push to array
});
```

Available update operators:
- `UpdateOp.set`: Set value
- `UpdateOp.inc`: Increment by value
- `UpdateOp.dec`: Decrement by value
- `UpdateOp.push`: Push to array
- `UpdateOp.pull`: Remove from array

### Temporary Databases for Testing

```typescript
// Create temporary database for tests
const testDataSource = await DataSource.fromTempDatabase({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  synchronize: true,
  entities: [User, Post]
});

// Run tests...

// Clear database after tests
await testDataSource.clearTempDatabase();

// Or clear all temp databases older than 1 hour
await dataSource.clearTempDatabasesOlderThan(3600);
```

## API Reference

### DataSource

```typescript
class DataSource {
  constructor(options: DataSourceOptions);
  
  // Connection management
  initialize(): Promise<this>;
  destroy(): Promise<void>;
  
  // Repositories
  getRepository<Entity>(entityClass: new (...args: any[]) => Entity): Repository<Entity>;
  
  // Query building
  createQueryBuilder(): AdaptedQueryBuilder;
  createEntityManager(queryRunner?: AdaptedQueryRunner): EntityManager;
  
  // Transactions
  transaction<T>(runInTransaction: (entityManager: EntityManager) => Promise<T>): Promise<T>;
  
  // Direct queries
  query(query: string, parameters?: any): Promise<any>;
  
  // Query runner
  createQueryRunner(): AdaptedQueryRunner;
  
  // Migrations
  runMigrations(): Promise<Array<{ name: string; status: string }>>;
  
  // Metadata
  getNeogma(): Neogma;
  getSubscribers(): Map<Function, EntitySubscriberInterface>;
  getMetadataByTarget(target: Function): EntityMetadata | undefined;
  registerSubscribers(): void;
  
  // Temporary database management (static methods)
  static fromTempDatabase(options: DataSourceOptions): Promise<DataSource>;
  clearTempDatabase(database?: string): Promise<void>;
  clearAllTempDatabases(): Promise<void>;
  clearTempDatabasesOlderThan(seconds: number): Promise<void>;
}
```

### Repository

```typescript
class Repository<Entity> {
  constructor(entityClass: new (...args: any[]) => Entity, dataSource: DataSource);
  
  // Query methods
  find(options?: FindOptions<Entity>): Promise<Entity[]>;
  findOne(options?: FindOneOptions<Entity>): Promise<Entity | null>;
  findOneById(id: string | number | Record<string, any>): Promise<Entity | null>;
  
  // Create and save
  create(entityLike: Partial<Entity>): Entity;
  save(entities: Entity | Entity[], options?: SaveOptions): Promise<Entity | Entity[]>;
  
  // Update
  update(id: string | number | Record<string, any>, partialEntity: Partial<Entity>): Promise<void>;
  
  // Delete
  softRemove(entities: Entity | Entity[]): Promise<Entity | Entity[]>;
  recover(entities: Entity | Entity[]): Promise<Entity | Entity[]>;
  
  // Count
  count(options?: FindOptions<Entity>): Promise<number>;
  
  // Upsert
  upsert(entityLike: Partial<Entity>, uniqueBy: (keyof Entity)[]): Promise<Entity>;
  
  // Query builder
  createQueryBuilder(): AdaptedQueryBuilder;
  
  // Helper methods
  hasId(entity: Entity): boolean;
  getId(entity: Entity): string | number | Record<string, any>;
}
```

### EntityManager

```typescript
class EntityManager {
  constructor(dataSource: DataSource, queryRunner?: AdaptedQueryRunner);
  
  // Repository management
  getRepository<Entity>(entityClass: new (...args: any[]) => Entity): Repository<Entity>;
  
  // Query execution
  query(query: string, parameters?: any): Promise<any>;
  createQueryBuilder(): AdaptedQueryBuilder;
  
  // Transactions
  transaction<T>(runInTransaction: (entityManager: EntityManager) => Promise<T>): Promise<T>;
  
  // Convenience methods that mirror Repository methods
  find<Entity>(entityClass: new (...args: any[]) => Entity, options?: FindOptions<Entity>): Promise<Entity[]>;
  findOne<Entity>(entityClass: new (...args: any[]) => Entity, options: FindOneOptions<Entity>): Promise<Entity | null>;
  findOneById<Entity>(entityClass: new (...args: any[]) => Entity, id: string | number | Record<string, any>): Promise<Entity | null>;
  create<Entity>(entityClass: new (...args: any[]) => Entity, entityLike: Partial<Entity>): Entity;
  save<Entity>(entityClass: new (...args: any[]) => Entity, entities: Entity | Entity[], options?: SaveOptions): Promise<Entity | Entity[]>;
  update<Entity>(entityClass: new (...args: any[]) => Entity, id: string | number | Record<string, any>, partialEntity: Partial<Entity>): Promise<void>;
  softRemove<Entity>(entityClass: new (...args: any[]) => Entity, entities: Entity | Entity[]): Promise<Entity | Entity[]>;
  recover<Entity>(entityClass: new (...args: any[]) => Entity, entities: Entity | Entity[]): Promise<Entity | Entity[]>;
  count<Entity>(entityClass: new (...args: any[]) => Entity, options?: FindOptions<Entity>): Promise<number>;
  upsert<Entity>(entityClass: new (...args: any[]) => Entity, entityLike: Partial<Entity>, uniqueBy: (keyof Entity)[]): Promise<Entity>;
}
```

### Logger

```typescript
enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3
}

class Logger {
  static get instance(): Logger;
  setLevel(level: LogLevel): void;
  debug(message: string, ...args: any[]): void;
  info(message: string, ...args: any[]): void;
  warn(message: string, ...args: any[]): void;
  error(message: string, ...args: any[]): void;
}
```

## Examples

### Complete User/Post/Comment Example

```typescript
import {
  DataSource,
  Entity,
  NodeId,
  Property,
  Relationship,
  CreateDateColumn,
  UpdateDateColumn,
  BeforeInsert,
  AfterInsert,
  Op
} from 'neo4j-orm';

// User entity
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property({ unique: true })
  email: string;

  @Property()
  firstName: string;

  @Property()
  lastName: string;

  @Property({ nullable: true })
  bio?: string;

  @Relationship({
    type: 'AUTHORED',
    direction: 'OUT',
    target: () => Post,
    cascade: true
  })
  posts: Post[];

  @Relationship({
    type: 'WROTE',
    direction: 'OUT',
    target: () => Comment
  })
  comments: Comment[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @BeforeInsert()
  normalizeEmail() {
    if (this.email) {
      this.email = this.email.toLowerCase().trim();
    }
  }

  // Getter for full name
  get fullName(): string {
    return `${this.firstName} ${this.lastName}`;
  }
}

// Post entity
@Entity()
class Post {
  @NodeId({ generated: true })
  id: string;

  @Property({ nullable: false })
  title: string;

  @Property()
  content: string;

  @Relationship({
    type: 'AUTHORED_BY',
    direction: 'OUT',
    target: User
  })
  author: User;

  @Relationship({
    type: 'HAS_COMMENT',
    direction: 'OUT',
    target: () => Comment,
    cascade: true
  })
  comments: Comment[];

  @Property({ default: 0 })
  viewCount: number;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

// Comment entity
@Entity()
class Comment {
  @NodeId({ generated: true })
  id: string;

  @Property()
  text: string;

  @Relationship({
    type: 'WRITTEN_BY',
    direction: 'OUT',
    target: User
  })
  author: User;

  @Relationship({
    type: 'BELONGS_TO',
    direction: 'OUT',
    target: Post
  })
  post: Post;

  @CreateDateColumn()
  createdAt: Date;
}

// Initialize DataSource
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User, Post, Comment],
  synchronize: true
});

async function example() {
  await dataSource.initialize();

  // Get repositories
  const userRepo = dataSource.getRepository(User);
  const postRepo = dataSource.getRepository(Post);
  const commentRepo = dataSource.getRepository(Comment);

  // Create user
  const user = userRepo.create({
    email: 'john@example.com',
    firstName: 'John',
    lastName: 'Doe',
    bio: 'Software developer'
  });

  await userRepo.save(user);
  console.log('User created:', user);

  // Create post
  const post = postRepo.create({
    title: 'Getting Started with Neo4j-ORM',
    content: 'This is a comprehensive guide to using Neo4j-ORM...',
    author: user
  });

  await postRepo.save(post);
  console.log('Post created:', post);

  // Create comment
  const comment = commentRepo.create({
    text: 'Great post!',
    author: user,
    post: post
  });

  await commentRepo.save(comment);
  console.log('Comment created:', comment);

  // Find posts with comments
  const posts = await postRepo.find({
    where: {},
    relations: ['author', 'comments', 'comments.author']
  });

  console.log('Posts with comments:', posts);

  // Query with QueryBuilder
  const queryBuilder = dataSource.createQueryBuilder();

  queryBuilder
    .match('u', User)
    .match({
      related: [
        { identifier: 'u' },
        { direction: 'out', name: 'AUTHORED' },
        { identifier: 'p', label: 'Post' }
      ]
    })
    .return('u.firstName, u.lastName, count(p) as postCount')
    .orderBy('postCount', 'DESC');

  const result = await queryBuilder.getRaw();
  console.log('User post counts:', result.records);

  // Clean up
  await dataSource.destroy();
}

example().catch(console.error);
```

### Advanced Query Example

```typescript
import { DataSource, Entity, NodeId, Property, Relationship, Op } from 'neo4j-orm';

async function advancedQueryExample() {
  const dataSource = await new DataSource({
    type: 'neo4j',
    host: 'localhost',
    port: 7687,
    username: 'neo4j',
    password: 'password',
    database: 'neo4j',
    entities: [User, Post, Category, Tag]
  }).initialize();

  const userRepo = dataSource.getRepository(User);
  const postRepo = dataSource.getRepository(Post);

  // Find users with complex conditions
  const users = await userRepo.find({
    where: {
      // Multiple conditions
      firstName: { [Op.contains]: 'Jo' },
      age: { [Op.gte]: 21 },
      lastName: { [Op.in]: ['Smith', 'Jones', 'Johnson'] },
      createdAt: { [Op.gte]: new Date('2023-01-01') },
      
      // You can also use plain values for exact matches
      isActive: true
    },
    // Load relationships
    relations: ['posts'],
    // Sorting
    order: [
      ['lastName', 'ASC'],
      ['firstName', 'ASC']
    ],
    // Pagination
    skip: 0,
    take: 10
  });

  // Find posts with a complex query builder
  const qb = postRepo.createQueryBuilder();

  qb.match('p', Post)
    .match({
      related: [
        { identifier: 'p' },
        { direction: 'out', name: 'BELONGS_TO' },
        { identifier: 'c', label: 'Category' }
      ]
    })
    .match({
      related: [
        { identifier: 'p' },
        { direction: 'out', name: 'TAGGED_WITH' },
        { identifier: 't', label: 'Tag' }
      ]
    })
    .match({
      related: [
        { identifier: 'p' },
        { direction: 'out', name: 'AUTHORED_BY' },
        { identifier: 'u', label: 'User' }
      ]
    })
    .where('c.name = $category')
    .andWhere('t.name IN $tags')
    .andWhere('p.createdAt >= $startDate')
    .andWhere('u.reputation > $minReputation')
    .with('p, u, collect(distinct t.name) as tags, c.name as category')
    .return('p, u, tags, category')
    .orderBy('p.createdAt', 'DESC')
    .limit(10);

  const posts = await qb.getRaw();

  // Using parameters
  const params = {
    category: 'Technology',
    tags: ['javascript', 'neo4j', 'graphdb'],
    startDate: new Date('2023-05-01'),
    minReputation: 100
  };

  // Add parameters to the query
  qb.neogmaQueryBuilder.getBindParam().add(params);

  const result = await qb.getRaw();

  // Clean up
  await dataSource.destroy();
}
```

### Transaction Example

```typescript
import { DataSource, Entity, NodeId, Property, Relationship } from 'neo4j-orm';

async function transactionExample() {
  const dataSource = await new DataSource({
    type: 'neo4j',
    host: 'localhost',
    port: 7687,
    username: 'neo4j',
    password: 'password',
    database: 'neo4j'
  }).initialize();

  try {
    // Using DataSource transaction
    const result = await dataSource.transaction(async (manager) => {
      // Get repositories within transaction
      const userRepo = manager.getRepository(User);
      const postRepo = manager.getRepository(Post);
      const commentRepo = manager.getRepository(Comment);
      
      // Create user
      const user = userRepo.create({
        email: 'alice@example.com',
        firstName: 'Alice',
        lastName: 'Smith'
      });
      await userRepo.save(user);
      
      // Create post
      const post = postRepo.create({
        title: 'My Transaction Example',
        content: 'This is a post created in a transaction',
        author: user
      });
      await postRepo.save(post);
      
      // Create comment
      const comment = commentRepo.create({
        text: 'First comment!',
        author: user,
        post: post
      });
      await commentRepo.save(comment);
      
      // Return created entities
      return { user, post, comment };
    });
    
    console.log('Transaction successful!', result);
    
    // Using EntityManager transaction
    const entityManager = dataSource.createEntityManager();
    
    const secondResult = await entityManager.transaction(async (transactionManager) => {
      // Perform operations with the transactionManager
      const user = await transactionManager.findOne(User, {
        where: { email: 'alice@example.com' }
      });
      
      if (user) {
        // Update user
        await transactionManager.update(User, user.id, {
          bio: 'Updated within a transaction'
        });
        
        // Create another post
        const post = transactionManager.create(Post, {
          title: 'Second Post',
          content: 'Another post in a transaction',
          author: user
        });
        await transactionManager.save(Post, post);
        
        return { user, post };
      }
      
      return null;
    });
    
    console.log('Second transaction successful!', secondResult);
  } catch (error) {
    console.error('Transaction failed:', error);
  } finally {
    await dataSource.destroy();
  }
}
```

### Subscriber Example

```typescript
import { 
  DataSource, 
  Entity, 
  NodeId, 
  Property,
  CreateDateColumn,
  EventSubscriber,
  EntitySubscriberInterface,
  InsertEvent,
  UpdateEvent 
} from 'neo4j-orm';

@Entity()
class User {
  @NodeId({ generated: true })
  id: string;
  
  @Property({ unique: true })
  email: string;
  
  @Property()
  name: string;
  
  @Property({ default: false })
  isVerified: boolean;
  
  @CreateDateColumn()
  createdAt: Date;
}

@EventSubscriber()
class UserSubscriber implements EntitySubscriberInterface<User> {
  // Specify which entity this subscriber listens to
  listenTo() {
    return User;
  }
  
  async beforeInsert(event: InsertEvent<User>) {
    console.log('BEFORE USER INSERTED:', event.entity);
    
    // Normalize email
    if (event.entity.email) {
      event.entity.email = event.entity.email.toLowerCase().trim();
    }
  }
  
  async afterInsert(event: InsertEvent<User>) {
    console.log('AFTER USER INSERTED:', event.entity);
    
    // Simulate sending a welcome email
    console.log(`Sending welcome email to ${event.entity.email}`);
    
    // You could also perform additional database operations
    const emailLogRepo = event.manager.getRepository(EmailLog);
    await emailLogRepo.save({
      userId: event.entity.id,
      type: 'welcome',
      sentAt: new Date()
    });
  }
  
  async beforeUpdate(event: UpdateEvent<User>) {
    console.log('BEFORE USER UPDATED:', event.entity);
    
    // Check if email is changing
    if (event.entity.email !== event.databaseEntity.email) {
      console.log(`Email changing from ${event.databaseEntity.email} to ${event.entity.email}`);
      event.entity.isVerified = false;
    }
  }
  
  async afterUpdate(event: UpdateEvent<User>) {
    console.log('AFTER USER UPDATED:', event.entity);
    
    // If email verification status changed, log it
    if (event.entity.isVerified !== event.databaseEntity.isVerified) {
      console.log(`User ${event.entity.id} verification status changed to ${event.entity.isVerified}`);
    }
  }
}

@Entity()
class EmailLog {
  @NodeId({ generated: true })
  id: string;
  
  @Property()
  userId: string;
  
  @Property()
  type: string;
  
  @Property()
  sentAt: Date;
}

async function subscriberExample() {
  const dataSource = new DataSource({
    type: 'neo4j',
    host: 'localhost',
    port: 7687,
    username: 'neo4j',
    password: 'password',
    database: 'neo4j',
    entities: [User, EmailLog],
    synchronize: true
  });
  
  await dataSource.initialize();
  
  try {
    const userRepo = dataSource.getRepository(User);
    
    // Create a new user - subscriber events will be triggered
    const user = userRepo.create({
      email: 'John.Doe@EXAMPLE.com',  // Will be normalized
      name: 'John Doe'
    });
    
    await userRepo.save(user);
    console.log('User saved:', user);
    
    // Update the user - subscriber events will be triggered
    user.email = 'john.new@example.com';
    await userRepo.save(user);
    console.log('User updated:', user);
    
    // Verify the user - subscriber events will be triggered
    await userRepo.update(user.id, { isVerified: true });
    
    // Get the updated user
    const updatedUser = await userRepo.findOneById(user.id);
    console.log('Updated user:', updatedUser);
  } finally {
    await dataSource.destroy();
  }
}
```

### Migration Example

```typescript
import { DataSource, MigrationInterface, AdaptedQueryRunner } from 'neo4j-orm';

// First migration - create user schema
export class CreateUserSchema20230101 implements MigrationInterface {
  async up(queryRunner: AdaptedQueryRunner): Promise<any> {
    await queryRunner.query(`
      CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE
    `);
    
    await queryRunner.query(`
      CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE
    `);
    
    await queryRunner.query(`
      CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.name)
    `);
  }
  
  async down(queryRunner: AdaptedQueryRunner): Promise<any> {
    await queryRunner.query(`
      DROP CONSTRAINT IF EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE
    `);
    
    await queryRunner.query(`
      DROP CONSTRAINT IF EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE
    `);
    
    await queryRunner.query(`
      DROP INDEX IF EXISTS FOR (u:User) ON (u.name)
    `);
  }
}

// Second migration - add user role
export class AddUserRole20230215 implements MigrationInterface {
  async up(queryRunner: AdaptedQueryRunner): Promise<any> {
    await queryRunner.query(`
      MATCH (u:User)
      WHERE NOT EXISTS(u.role)
      SET u.role = 'user'
    `);
    
    await queryRunner.query(`
      CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.role)
    `);
  }
  
  async down(queryRunner: AdaptedQueryRunner): Promise<any> {
    await queryRunner.query(`
      MATCH (u:User)
      WHERE EXISTS(u.role)
      REMOVE u.role
    `);
    
    await queryRunner.query(`
      DROP INDEX IF EXISTS FOR (u:User) ON (u.role)
    `);
  }
}

// Running migrations
async function runMigrations() {
  const dataSource = new DataSource({
    type: 'neo4j',
    host: 'localhost',
    port: 7687,
    username: 'neo4j',
    password: 'password',
    database: 'neo4j',
    migrations: [
      CreateUserSchema20230101,
      AddUserRole20230215
    ]
  });
  
  await dataSource.initialize();
  
  try {
    const migrationResults = await dataSource.runMigrations();
    console.log('Migrations applied:', migrationResults);
  } finally {
    await dataSource.destroy();
  }
}
```

## Performance Best Practices

1. **Optimize Queries**:
   - Use specific MATCH patterns rather than broad ones
   - Filter early in the query to reduce the working set
   - Use parameters instead of string concatenation
   - Use EXPLAIN and PROFILE to analyze query performance

2. **Efficient Repository Use**:
   - Use `findOne` instead of `find` when you only need one record
   - Limit relationships with `relations` only to those you need
   - Use pagination with `skip` and `take` for large result sets

3. **Transactions**:
   - Keep transactions short and focused
   - Avoid executing many small operations in a loop; batch where possible
   - Use the transaction manager for all operations within a transaction

4. **Relationship Loading**:
   - Use eager loading only when necessary
   - Load relationships only when needed with the `relations` option
   - Consider using separate queries for very large relationship collections

5. **Indices and Constraints**:
   - Create indices on properties used frequently in WHERE clauses
   - Use `@Unique` and unique constraints for properties that should be unique
   - Consider composite indices for frequently combined filters

## Common Pitfalls and Solutions

1. **Circular Dependencies**:
   - Use `() => EntityClass` for relationship targets to avoid circular dependencies
   ```typescript
   @Relationship({
     type: 'AUTHORED',
     direction: 'OUT',
     target: () => Post // Lazy reference
   })
   posts: Post[];
   ```

2. **Transaction Management**:
   - Always use the transaction manager provided to the transaction callback
   - Don't mix transactional and non-transactional operations

3. **N+1 Query Problem**:
   - Load relationships eagerly or specify them in the `relations` option
   - Use QueryBuilder for complex queries with multiple relationships

4. **Memory Management**:
   - Be cautious with large result sets
   - Use pagination for large collections
   - Close connections when done with `dataSource.destroy()`

5. **Type Safety**:
   - Use TypeScript interfaces and types to ensure type safety
   - Use generics with repositories and query methods

## Conclusion

Neo4j-ORM provides a powerful, TypeORM-like interface for working with Neo4j graph databases in TypeScript/JavaScript applications. By combining the flexibility of graph databases with the familiarity of an ORM, developers can efficiently build and maintain graph-based applications while leveraging the full power of Neo4j.

For more information and detailed API documentation, visit the official Neo4j-ORM documentation site or GitHub repository.

---
*Note: This documentation covers Neo4j-ORM version 1.0.0 and may not reflect changes in newer versions.*