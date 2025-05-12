# Repository API Reference

The Repository pattern in Neo4j-ORM provides methods to interact with entities in the database. Each entity has its own repository that handles entity-specific operations.

## Getting a Repository

```typescript
// From DataSource
const userRepository = dataSource.getRepository(User);

// From EntityManager
const entityManager = dataSource.createEntityManager();
const userRepository = entityManager.getRepository(User);

// Within a transaction
await dataSource.transaction(async manager => {
  const userRepository = manager.getRepository(User);
  // Use the repository...
});
```

## Repository Methods

### create

```typescript
create(entityLike: Partial<Entity>): Entity
```

Creates a new entity instance.

**Parameters:**
- `entityLike`: An object with entity properties

**Returns:**
- A new entity instance (not saved to the database yet)

**Example:**
```typescript
const user = userRepository.create({
  name: 'John Doe',
  email: 'john@example.com',
  age: 30
});

// Entity is created in memory only, not in the database
console.log(user); // User { name: 'John Doe', email: 'john@example.com', age: 30 }
```

### save

```typescript
async save(entities: Entity | Entity[], options?: SaveOptions): Promise<Entity | Entity[]>
```

Saves one or more entities to the database.

**Parameters:**
- `entities`: A single entity or an array of entities to save
- `options` (optional): Save options

**Returns:**
- The saved entity or entities

**Default behavior:**
- Creates a new entity if it doesn't exist (no ID)
- Updates an existing entity if it exists (has ID)
- Does not save related entities unless cascading is enabled

**Example:**
```typescript
// Create and save a single entity
const user = userRepository.create({ name: 'John Doe', email: 'john@example.com' });
await userRepository.save(user);
console.log(user.id); // Generated ID

// Save multiple entities
const users = [
  userRepository.create({ name: 'Alice', email: 'alice@example.com' }),
  userRepository.create({ name: 'Bob', email: 'bob@example.com' })
];
await userRepository.save(users);

// Update an existing entity
user.name = 'John Smith';
await userRepository.save(user);
```

### SaveOptions Interface

```typescript
type SaveOptions = {
  saveRelations?: boolean; // Whether to save related entities
  depth?: number;          // How deep to traverse relationships
};
```

### find

```typescript
async find(options?: FindOptions<Entity>): Promise<Entity[]>
```

Finds entities that match the given criteria.

**Parameters:**
- `options` (optional): Find options

**Returns:**
- An array of entities that match the criteria

**Default behavior:**
- Returns all entities if no options are provided
- Does not load relationships unless specified

**Example:**
```typescript
// Find all users
const allUsers = await userRepository.find();

// Find with conditions
const activeAdults = await userRepository.find({
  where: {
    age: { [Op.gte]: 18 },
    active: true
  }
});

// Find with ordering
const sortedUsers = await userRepository.find({
  order: [['lastName', 'ASC'], ['firstName', 'ASC']]
});

// Find with pagination
const page = await userRepository.find({
  skip: 20,  // Skip first 20 results
  take: 10   // Take 10 results
});

// Find with relationships
const usersWithPosts = await userRepository.find({
  relations: ['posts', 'profile']
});

// Combined options
const result = await userRepository.find({
  where: { country: 'USA' },
  relations: ['orders'],
  order: [['createdAt', 'DESC']],
  skip: 0,
  take: 10
});
```

### FindOptions Interface

```typescript
interface FindOptions<Entity> {
  where?: Partial<Entity> | any;                        // Filter conditions
  relations?: string[];                                 // Relationships to load
  skip?: number;                                        // Number of results to skip
  take?: number;                                        // Number of results to take
  order?: [keyof Entity | string, 'ASC' | 'DESC'][];    // Sort order
}
```

### findOne

```typescript
async findOne(options: FindOneOptions<Entity> = {}): Promise<Entity | null>
```

Finds a single entity that matches the given criteria.

**Parameters:**
- `options`: Find options

**Returns:**
- The found entity, or null if not found

**Default behavior:**
- Returns the first entity that matches the criteria
- Does not load relationships unless specified

**Example:**
```typescript
// Find by email (unique property)
const user = await userRepository.findOne({
  where: { email: 'john@example.com' }
});

// Find with relationships
const userWithProfile = await userRepository.findOne({
  where: { id: '123' },
  relations: ['profile', 'posts']
});

// Find with ordering
const oldestUser = await userRepository.findOne({
  order: [['age', 'DESC']]
});
```

### FindOneOptions Interface

```typescript
interface FindOneOptions<Entity> {
  where?: Partial<Entity> | any;                        // Filter conditions
  relations?: string[];                                 // Relationships to load
  order?: [keyof Entity | string, 'ASC' | 'DESC'][];    // Sort order
}
```

### findOneById

```typescript
async findOneById(id: string | number | Record<string, any>): Promise<Entity | null>
```

Finds an entity by its ID.

**Parameters:**
- `id`: The entity ID or a record with ID fields for composite IDs

**Returns:**
- The found entity, or null if not found

**Default behavior:**
- Looks for an entity with the given ID
- Uses the property marked with `@NodeId()` as the ID

**Example:**
```typescript
// Find by string ID
const user = await userRepository.findOneById('123');

// Find by number ID
const product = await productRepository.findOneById(456);

// Find by composite ID
const employee = await employeeRepository.findOneById({
  companyId: 'company1',
  employeeNumber: 'E12345'
});
```

### update

```typescript
async update(id: string | number | Record<string, any>, partialEntity: Partial<Entity>): Promise<void>
```

Updates an entity by its ID.

**Parameters:**
- `id`: The entity ID or a record with ID fields for composite IDs
- `partialEntity`: An object with the properties to update

**Returns:**
- A Promise that resolves when the update is complete

**Default behavior:**
- Updates only the specified properties
- Does not return the updated entity

**Example:**
```typescript
// Update by ID
await userRepository.update('123', {
  name: 'John Smith',
  age: 31
});

// Update by composite ID
await employeeRepository.update(
  { companyId: 'company1', employeeNumber: 'E12345' },
  { position: 'Senior Developer', salary: 85000 }
);

// Update with operators
await productRepository.update('456', {
  stock: { [UpdateOp.inc]: 10 },        // Increment by 10
  viewCount: { [UpdateOp.inc]: 1 },     // Increment by 1
  categories: { [UpdateOp.push]: 'new'} // Add to array
});
```

### remove

```typescript
async remove(entities: Entity | Entity[]): Promise<Entity | Entity[]>
```

Removes one or more entities from the database.

**Parameters:**
- `entities`: A single entity or an array of entities to remove

**Returns:**
- The removed entity or entities

**Default behavior:**
- Permanently deletes the entity from the database
- Does not remove related entities unless cascading is enabled

**Example:**
```typescript
// Remove a single entity
const user = await userRepository.findOneById('123');
if (user) {
  await userRepository.remove(user);
}

// Remove multiple entities
const inactiveUsers = await userRepository.find({
  where: { active: false }
});
await userRepository.remove(inactiveUsers);
```

### softRemove

```typescript
async softRemove(entities: Entity | Entity[]): Promise<Entity | Entity[]>
```

Soft removes (marks as deleted) one or more entities.

**Parameters:**
- `entities`: A single entity or an array of entities to soft remove

**Returns:**
- The soft-removed entity or entities

**Default behavior:**
- Sets the delete date column to the current date
- Entity is not actually deleted from the database
- Entity will be excluded from regular find operations

**Requirements:**
- Entity must have a property decorated with `@DeleteDateColumn()`

**Example:**
```typescript
@Entity()
class User {
  @NodeId()
  id: string;

  @Property()
  name: string;

  @DeleteDateColumn()
  deletedAt: Date;
}

// Soft remove a user
const user = await userRepository.findOneById('123');
if (user) {
  await userRepository.softRemove(user);
  // user.deletedAt is now set to the current date
}
```

### recover

```typescript
async recover(entities: Entity | Entity[]): Promise<Entity | Entity[]>
```

Recovers soft-removed entities.

**Parameters:**
- `entities`: A single entity or an array of entities to recover

**Returns:**
- The recovered entity or entities

**Default behavior:**
- Sets the delete date column to null
- Makes the entity visible in regular find operations again

**Requirements:**
- Entity must have a property decorated with `@DeleteDateColumn()`

**Example:**
```typescript
// Recover a soft-removed user
const user = await userRepository.findOneById('123', {
  withDeleted: true // Option to include soft-deleted entities
});
if (user && user.deletedAt) {
  await userRepository.recover(user);
  // user.deletedAt is now null
}
```

### count

```typescript
async count(options?: FindOptions<Entity>): Promise<number>
```

Counts entities that match the given criteria.

**Parameters:**
- `options` (optional): Find options

**Returns:**
- The number of entities that match the criteria

**Example:**
```typescript
// Count all users
const totalUsers = await userRepository.count();

// Count with conditions
const activeUserCount = await userRepository.count({
  where: { active: true }
});

// Count with complex conditions
const premiumUserCount = await userRepository.count({
  where: {
    subscriptionType: 'premium',
    subscriptionEndDate: { [Op.gt]: new Date() }
  }
});
```

### upsert

```typescript
async upsert(
  entityLike: Partial<Entity>,
  uniqueBy: (keyof Entity)[]
): Promise<Entity>
```

Creates or updates an entity based on unique properties.

**Parameters:**
- `entityLike`: An object with entity properties
- `uniqueBy`: Property names to use for determining uniqueness

**Returns:**
- The created or updated entity

**Default behavior:**
- If an entity with the specified unique properties exists, updates it
- If no matching entity exists, creates a new one

**Example:**
```typescript
// Upsert a user by email
const user = await userRepository.upsert(
  {
    email: 'john@example.com',
    name: 'John Doe',
    lastLogin: new Date()
  },
  ['email'] // Unique property to match by
);

// Upsert by composite unique properties
const product = await productRepository.upsert(
  {
    sku: 'ABC123',
    manufacturer: 'Acme',
    name: 'Widget Pro',
    price: 29.99,
    stock: 100
  },
  ['sku', 'manufacturer'] // Composite unique properties
);
```

### createQueryBuilder

```typescript
createQueryBuilder(): AdaptedQueryBuilder
```

Creates a new query builder for the entity.

**Returns:**
- A new QueryBuilder instance

**Example:**
```typescript
const queryBuilder = userRepository.createQueryBuilder();

queryBuilder
  .match('u', User)
  .where('u.active = true')
  .return('u')
  .orderBy('u.name', 'ASC')
  .limit(10);

const users = await queryBuilder.getMany();
```

## Using Where Conditions

The `where` option in find methods supports various conditions:

### Simple Equality

```typescript
// Find users with name 'John'
const users = await userRepository.find({
  where: { name: 'John' }
});
```

### Using Operators

```typescript
import { Op } from 'neo4j-orm';

// Find users older than 21
const adults = await userRepository.find({
  where: {
    age: { [Op.gt]: 21 }
  }
});

// Find users between 18 and 65
const users = await userRepository.find({
  where: {
    age: {
      [Op.gte]: 18,
      [Op.lte]: 65
    }
  }
});

// Find users with specific names
const specificUsers = await userRepository.find({
  where: {
    name: { [Op.in]: ['John', 'Alice', 'Bob'] }
  }
});

// Find users with email containing a domain
const companyUsers = await userRepository.find({
  where: {
    email: { [Op.contains]: '@company.com' }
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
- `Op.contains`: Contains substring
- `Op.startsWith`: Starts with substring
- `Op.endsWith`: Ends with substring

### Combined Conditions

```typescript
// Multiple conditions (AND)
const users = await userRepository.find({
  where: {
    age: { [Op.gte]: 18 },
    country: 'USA',
    active: true
  }
});
```

For more complex conditions, use the QueryBuilder.

## Working with Relationships

### Loading Relationships

```typescript
// Load direct relationships
const userWithPosts = await userRepository.findOne({
  where: { id: '123' },
  relations: ['posts', 'profile']
});

// Load nested relationships
const userWithNestedRelations = await userRepository.findOne({
  where: { id: '123' },
  relations: ['posts', 'posts.comments', 'posts.comments.author']
});
```

### Creating Entities with Relationships

```typescript
// Create a user with posts
const user = userRepository.create({
  name: 'Jane Doe',
  email: 'jane@example.com'
});

const post1 = postRepository.create({
  title: 'First Post',
  content: 'Hello, world!'
});

const post2 = postRepository.create({
  title: 'Second Post',
  content: 'More content here'
});

// Set the relationship
user.posts = [post1, post2];

// Save the user with cascading to save posts too
await userRepository.save(user, { saveRelations: true });
```

### Updating Related Entities

```typescript
// Update related entities
const user = await userRepository.findOne({
  where: { id: '123' },
  relations: ['posts']
});

if (user && user.posts) {
  // Update a related entity
  user.posts[0].title = 'Updated Title';
  
  // Save with cascading
  await userRepository.save(user, { saveRelations: true });
}
```

## Best Practices

1. **Use typed repositories:**
   ```typescript
   const userRepository: Repository<User> = dataSource.getRepository(User);
   ```

2. **Prefer `findOne` over `find` when you only need one result:**
   ```typescript
   // Better
   const user = await userRepository.findOne({ where: { email } });
   
   // Less efficient
   const users = await userRepository.find({ where: { email } });
   const user = users[0];
   ```

3. **Use QueryBuilder for complex queries:**
   ```typescript
   const qb = userRepository.createQueryBuilder();
   // Build complex query...
   ```

4. **Handle null/undefined correctly:**
   ```typescript
   const user = await userRepository.findOneById(id);
   if (!user) {
     throw new Error('User not found');
   }
   ```

5. **Use transactions for multiple operations:**
   ```typescript
   await dataSource.transaction(async manager => {
     const userRepo = manager.getRepository(User);
     const postRepo = manager.getRepository(Post);
     
     // Multiple operations within a transaction
   });
   ```

This concludes the Repository API reference.