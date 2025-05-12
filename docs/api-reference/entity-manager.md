# EntityManager API Reference

The EntityManager is a higher-level API for working with entities across multiple repositories. It provides a unified interface for database operations and supports transactions.

## Getting an EntityManager

```typescript
// From DataSource
const entityManager = dataSource.createEntityManager();

// In a transaction
await dataSource.transaction(async manager => {
  // manager is an EntityManager instance
  // Use it for operations within the transaction
});
```

## Core Methods

### getRepository

```typescript
getRepository<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity
): Repository<Entity>
```

Gets a repository for the specified entity class.

**Parameters:**
- `entityClass`: The entity class

**Returns:**
- A Repository instance for the entity

**Example:**
```typescript
const userRepository = entityManager.getRepository(User);
const postRepository = entityManager.getRepository(Post);

// Use the repositories
const user = await userRepository.findOne({ where: { email: 'john@example.com' } });
```

### query

```typescript
async query(query: string, parameters?: any): Promise<any>
```

Executes a raw Cypher query.

**Parameters:**
- `query`: The Cypher query string
- `parameters` (optional): Query parameters

**Returns:**
- A Promise that resolves to the query result

**Example:**
```typescript
const result = await entityManager.query(
  'MATCH (u:User {email: $email}) RETURN u',
  { email: 'john@example.com' }
);
```

### createQueryBuilder

```typescript
createQueryBuilder(): AdaptedQueryBuilder
```

Creates a new query builder.

**Returns:**
- A new QueryBuilder instance

**Example:**
```typescript
const queryBuilder = entityManager.createQueryBuilder();

queryBuilder
  .match('u', User)
  .return('u');

const users = await queryBuilder.getMany();
```

### transaction

```typescript
async transaction<T>(
  runInTransaction: (entityManager: EntityManager) => Promise<T>
): Promise<T>
```

Executes the given function in a transaction.

**Parameters:**
- `runInTransaction`: A function that receives a transaction-bound EntityManager and returns a Promise

**Returns:**
- A Promise that resolves to the result of the transaction function

**Throws:**
- Error if already in a transaction
- Any error thrown by the transaction function (causing rollback)

**Example:**
```typescript
const result = await entityManager.transaction(async transactionManager => {
  const user = transactionManager.create(User, { name: 'Alice' });
  await transactionManager.save(user);
  return user;
});
```

## Entity Operations

The EntityManager provides methods that mirror Repository methods but require an entity class as the first parameter:

### find

```typescript
async find<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  options?: FindOptions<Entity>
): Promise<Entity[]>
```

Finds entities that match the given criteria.

**Parameters:**
- `entityClass`: The entity class
- `options` (optional): Find options

**Returns:**
- A Promise that resolves to an array of entities

**Example:**
```typescript
const activeUsers = await entityManager.find(User, {
  where: { active: true }
});
```

### findOne

```typescript
async findOne<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  options: FindOneOptions<Entity>
): Promise<Entity | null>
```

Finds a single entity that matches the given criteria.

**Parameters:**
- `entityClass`: The entity class
- `options`: Find options

**Returns:**
- A Promise that resolves to an entity or null if not found

**Example:**
```typescript
const user = await entityManager.findOne(User, {
  where: { email: 'john@example.com' }
});
```

### findOneById

```typescript
async findOneById<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  id: string | number | Record<string, any>
): Promise<Entity | null>
```

Finds an entity by its ID.

**Parameters:**
- `entityClass`: The entity class
- `id`: The entity ID or a record with ID fields for composite IDs

**Returns:**
- A Promise that resolves to an entity or null if not found

**Example:**
```typescript
const user = await entityManager.findOneById(User, '123');
```

### create

```typescript
create<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  entityLike: Partial<Entity>
): Entity
```

Creates a new entity instance.

**Parameters:**
- `entityClass`: The entity class
- `entityLike`: An object with entity properties

**Returns:**
- A new entity instance (not saved to the database yet)

**Example:**
```typescript
const user = entityManager.create(User, {
  name: 'John Doe',
  email: 'john@example.com'
});
```

### save

```typescript
async save<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  entities: Entity | Entity[],
  options?: SaveOptions
): Promise<Entity | Entity[]>
```

Saves one or more entities to the database.

**Parameters:**
- `entityClass`: The entity class
- `entities`: A single entity or an array of entities to save
- `options` (optional): Save options

**Returns:**
- A Promise that resolves to the saved entity or entities

**Example:**
```typescript
// Create and save in one step
const user = await entityManager.save(User, {
  name: 'John Doe',
  email: 'john@example.com'
});

// Save multiple entities
await entityManager.save(User, [
  { name: 'Alice', email: 'alice@example.com' },
  { name: 'Bob', email: 'bob@example.com' }
]);
```

### update

```typescript
async update<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  id: string | number | Record<string, any>,
  partialEntity: Partial<Entity>
): Promise<void>
```

Updates an entity by its ID.

**Parameters:**
- `entityClass`: The entity class
- `id`: The entity ID or a record with ID fields for composite IDs
- `partialEntity`: An object with the properties to update

**Returns:**
- A Promise that resolves when the update is complete

**Example:**
```typescript
await entityManager.update(User, '123', {
  name: 'John Smith',
  age: 31
});
```

### softRemove

```typescript
async softRemove<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  entities: Entity | Entity[]
): Promise<Entity | Entity[]>
```

Soft removes (marks as deleted) one or more entities.

**Parameters:**
- `entityClass`: The entity class
- `entities`: A single entity or an array of entities to soft remove

**Returns:**
- A Promise that resolves to the soft-removed entity or entities

**Example:**
```typescript
const user = await entityManager.findOneById(User, '123');
if (user) {
  await entityManager.softRemove(User, user);
}
```

### recover

```typescript
async recover<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  entities: Entity | Entity[]
): Promise<Entity | Entity[]>
```

Recovers soft-removed entities.

**Parameters:**
- `entityClass`: The entity class
- `entities`: A single entity or an array of entities to recover

**Returns:**
- A Promise that resolves to the recovered entity or entities

**Example:**
```typescript
const user = await entityManager.findOneById(User, '123', {
  withDeleted: true
});
if (user && user.deletedAt) {
  await entityManager.recover(User, user);
}
```

### count

```typescript
async count<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  options?: FindOptions<Entity>
): Promise<number>
```

Counts entities that match the given criteria.

**Parameters:**
- `entityClass`: The entity class
- `options` (optional): Find options

**Returns:**
- A Promise that resolves to the number of entities

**Example:**
```typescript
const activeUserCount = await entityManager.count(User, {
  where: { active: true }
});
```

### upsert

```typescript
async upsert<Entity extends Record<string, any>>(
  entityClass: new (...args: any[]) => Entity,
  entityLike: Partial<Entity>,
  uniqueBy: (keyof Entity)[]
): Promise<Entity>
```

Creates or updates an entity based on unique properties.

**Parameters:**
- `entityClass`: The entity class
- `entityLike`: An object with entity properties
- `uniqueBy`: Property names to use for determining uniqueness

**Returns:**
- A Promise that resolves to the created or updated entity

**Example:**
```typescript
const user = await entityManager.upsert(User, {
  email: 'john@example.com',
  name: 'John Doe',
  lastLogin: new Date()
}, ['email']);
```

## Using EntityManager for Multiple Operations

The EntityManager is particularly useful when working with multiple entity types:

```typescript
// Create related entities
const user = entityManager.create(User, {
  name: 'Jane',
  email: 'jane@example.com'
});
await entityManager.save(User, user);

const post = entityManager.create(Post, {
  title: 'My First Post',
  content: 'Hello, world!',
  author: user
});
await entityManager.save(Post, post);

const comment = entityManager.create(Comment, {
  text: 'Great post!',
  post: post,
  author: user
});
await entityManager.save(Comment, comment);
```

## Transactions

Transactions ensure that a series of operations succeed or fail as a unit:

```typescript
await entityManager.transaction(async transactionManager => {
  // Get repositories
  const userRepo = transactionManager.getRepository(User);
  const postRepo = transactionManager.getRepository(Post);

  // Create user
  const user = userRepo.create({ name: 'Alice', email: 'alice@example.com' });
  await userRepo.save(user);

  // Create post
  const post = postRepo.create({ 
    title: 'My Transaction Example', 
    content: 'Using transactions...', 
    author: user 
  });
  await postRepo.save(post);

  // If any operation fails, the entire transaction is rolled back
});
```

You can also use the `transaction` method directly from the DataSource:

```typescript
await dataSource.transaction(async manager => {
  // manager is an EntityManager
  const user = await manager.save(User, { name: 'Bob', email: 'bob@example.com' });
  await manager.save(Post, { title: 'Transaction Demo', author: user });
});
```

## Nested Transactions

Neo4j-ORM doesn't support nested transactions. Trying to start a transaction from within a transaction will throw an error:

```typescript
// This will throw an error
await dataSource.transaction(async outerManager => {
  // This inner transaction will fail
  await outerManager.transaction(async innerManager => {
    // ...
  });
});
```

Instead, perform all operations within a single transaction:

```typescript
await dataSource.transaction(async manager => {
  // Perform all operations using this manager
});
```

## Best Practices

1. **Use repositories for entity-specific operations:**
   ```typescript
   const userRepository = entityManager.getRepository(User);
   const users = await userRepository.find({ where: { active: true } });
   ```

2. **Use EntityManager for cross-entity operations:**
   ```typescript
   // More concise than getting individual repositories
   const user = await entityManager.findOneById(User, userId);
   const posts = await entityManager.find(Post, { where: { author: user } });
   ```

3. **Always use transactions for multiple write operations:**
   ```typescript
   await entityManager.transaction(async manager => {
     // Multiple write operations...
   });
   ```

4. **Handle errors in transactions:**
   ```typescript
   try {
     await entityManager.transaction(async manager => {
       // Operations that might fail...
     });
     console.log('Transaction succeeded');
   } catch (error) {
     console.error('Transaction failed:', error);
   }
   ```

5. **Release resources:**
   ```typescript
   try {
     // Use EntityManager...
   } finally {
     // If you created a custom EntityManager, release it
     if (customEntityManager) {
       await customEntityManager.release();
     }
   }
   ```

This concludes the EntityManager API reference.
