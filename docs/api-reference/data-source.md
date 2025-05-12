# DataSource API Reference

The `DataSource` class is the main entry point for connecting to a Neo4j database. It manages the connection, provides access to repositories, and handles transactions.

## Constructor

```typescript
constructor(options: DataSourceOptions)
```

Creates a new DataSource instance with the specified options.

**Parameters:**
- `options`: Configuration options for the data source

**Returns:**
- A new DataSource instance (not yet initialized)

**Example:**
```typescript
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User, Post],
  synchronize: true
});
```

## DataSourceOptions

The `DataSourceOptions` interface defines the configuration for a DataSource:

```typescript
interface DataSourceOptions {
  type: string;                // Database type, always 'neo4j'
  host: string;                // Database host
  port: number;                // Database port
  username: string;            // Database username
  password: string;            // Database password
  database?: string;           // Database name (optional)
  entities?: Function[];       // Entity classes
  migrations?: string[];       // Migration paths or classes
  logging?: boolean;           // Enable query logging
  synchronize?: boolean;       // Auto-create constraints and indices
}
```

## Methods

### initialize()

```typescript
async initialize(): Promise<this>
```

Initializes the connection to the Neo4j database.

**Returns:**
- A Promise that resolves to the DataSource instance

**Throws:**
- `ConnectionError`: If connection fails

**Example:**
```typescript
await dataSource.initialize();
```

### destroy()

```typescript
async destroy(): Promise<void>
```

Closes the connection to the Neo4j database.

**Returns:**
- A Promise that resolves when the connection is closed

**Example:**
```typescript
await dataSource.destroy();
```

### getRepository()

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

**Throws:**
- `ConnectionError`: If DataSource is not initialized

**Example:**
```typescript
const userRepository = dataSource.getRepository(User);
```

### createQueryBuilder()

```typescript
createQueryBuilder(): AdaptedQueryBuilder
```

Creates a new query builder.

**Returns:**
- A new QueryBuilder instance

**Throws:**
- `ConnectionError`: If DataSource is not initialized

**Example:**
```typescript
const queryBuilder = dataSource.createQueryBuilder();
```

### createEntityManager()

```typescript
createEntityManager(queryRunner?: AdaptedQueryRunner): EntityManager
```

Creates a new entity manager.

**Parameters:**
- `queryRunner` (optional): A query runner to use

**Returns:**
- A new EntityManager instance

**Throws:**
- `ConnectionError`: If DataSource is not initialized

**Example:**
```typescript
const entityManager = dataSource.createEntityManager();
```

### transaction()

```typescript
async transaction<T>(
  runInTransaction: (entityManager: EntityManager) => Promise<T>
): Promise<T>
```

Executes the given function in a transaction.

**Parameters:**
- `runInTransaction`: A function that receives an EntityManager and returns a Promise

**Returns:**
- A Promise that resolves to the result of the transaction function

**Throws:**
- `ConnectionError`: If DataSource is not initialized
- Any error thrown by the transaction function (causing rollback)

**Example:**
```typescript
const result = await dataSource.transaction(async manager => {
  const user = manager.create(User, { name: 'Alice' });
  await manager.save(user);
  return user;
});
```

### query()

```typescript
async query(query: string, parameters?: any): Promise<any>
```

Executes a raw Cypher query.

**Parameters:**
- `query`: The Cypher query string
- `parameters` (optional): Query parameters

**Returns:**
- A Promise that resolves to the query result

**Throws:**
- `ConnectionError`: If DataSource is not initialized
- `QueryError`: If the query fails

**Example:**
```typescript
const result = await dataSource.query(
  'MATCH (u:User {email: $email}) RETURN u',
  { email: 'alice@example.com' }
);
```

### createQueryRunner()

```typescript
createQueryRunner(): AdaptedQueryRunner
```

Creates a new query runner.

**Returns:**
- A new QueryRunner instance

**Throws:**
- `ConnectionError`: If DataSource is not initialized

**Example:**
```typescript
const queryRunner = dataSource.createQueryRunner();
```

### runMigrations()

```typescript
async runMigrations(): Promise<Array<{ name: string; status: string }>>
```

Runs all pending migrations.

**Returns:**
- A Promise that resolves to an array of migration results

**Throws:**
- `ConnectionError`: If DataSource is not initialized

**Example:**
```typescript
const migrations = await dataSource.runMigrations();
console.log('Migrations applied:', migrations);
```

### getNeogma()

```typescript
getNeogma(): Neogma
```

Gets the underlying Neogma instance.

**Returns:**
- The Neogma instance

**Example:**
```typescript
const neogma = dataSource.getNeogma();
```

### Static Methods

#### fromTempDatabase()

```typescript
static async fromTempDatabase(options: DataSourceOptions): Promise<DataSource>
```

Creates a temporary database for testing.

**Parameters:**
- `options`: Configuration options for the data source

**Returns:**
- A Promise that resolves to a new DataSource instance

**Example:**
```typescript
const testDataSource = await DataSource.fromTempDatabase({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password'
});
```

### Temporary Database Methods

#### clearTempDatabase()

```typescript
async clearTempDatabase(database?: string): Promise<void>
```

Clears a temporary database.

**Parameters:**
- `database` (optional): The name of the database to clear

**Returns:**
- A Promise that resolves when the database is cleared

**Throws:**
- Error if the database name doesn't start with 'temp_'

**Example:**
```typescript
await dataSource.clearTempDatabase();
```

#### clearAllTempDatabases()

```typescript
async clearAllTempDatabases(): Promise<void>
```

Clears all temporary databases.

**Returns:**
- A Promise that resolves when all temporary databases are cleared

**Example:**
```typescript
await dataSource.clearAllTempDatabases();
```

#### clearTempDatabasesOlderThan()

```typescript
async clearTempDatabasesOlderThan(seconds: number): Promise<void>
```

Clears temporary databases older than the specified number of seconds.

**Parameters:**
- `seconds`: Age threshold in seconds

**Returns:**
- A Promise that resolves when the databases are cleared

**Example:**
```typescript
// Clear temp databases older than 1 hour
await dataSource.clearTempDatabasesOlderThan(3600);
```

## Usage Examples

### Basic Connection

```typescript
// Create a DataSource
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User, Post],
  synchronize: true
});

// Connect
await dataSource.initialize();
console.log('Connected to Neo4j');

// Perform operations...

// Close the connection
await dataSource.destroy();
```

### Using Repositories

```typescript
// Initialize the DataSource
await dataSource.initialize();

// Get repositories for different entities
const userRepo = dataSource.getRepository(User);
const postRepo = dataSource.getRepository(Post);

// Use the repositories
const user = await userRepo.findOne({ where: { email: 'john@example.com' } });
const posts = await postRepo.find({ where: { author: user } });
```

### Using Transactions

```typescript
const result = await dataSource.transaction(async manager => {
  // Get repositories within the transaction
  const userRepo = manager.getRepository(User);
  const postRepo = manager.getRepository(Post);

  // Create user
  const user = userRepo.create({ name: 'Jane', email: 'jane@example.com' });
  await userRepo.save(user);

  // Create post
  const post = postRepo.create({ title: 'My Post', content: 'Hello world', author: user });
  await postRepo.save(post);

  return { user, post };
});
```

### Running Migrations

```typescript
// Configure DataSource with migrations
const dataSource = new DataSource({
  // ... connection options
  migrations: [
    'src/migrations/*.js' // Path to migration files
  ]
});

// Initialize
await dataSource.initialize();

// Run migrations
const migrations = await dataSource.runMigrations();
console.log('Applied migrations:', migrations);
```

### Using Raw Queries

```typescript
// Execute a raw Cypher query
const result = await dataSource.query(`
  MATCH (u:User)-[:AUTHORED]->(p:Post)
  WHERE u.email = $email
  RETURN u, collect(p) as posts
`, { email: 'john@example.com' });

// Process the results
console.log('User:', result.records[0].get('u').properties);
console.log('Posts:', result.records[0].get('posts').map(p => p.properties));
```

## Error Handling

```typescript
try {
  await dataSource.initialize();
  // Perform operations...
} catch (error) {
  if (error instanceof ConnectionError) {
    console.error('Failed to connect to the database:', error.message);
    // Handle connection error
  } else if (error instanceof QueryError) {
    console.error('Query error:', error.message);
    console.error('Query:', error.query);
    // Handle query error
  } else {
    console.error('Unexpected error:', error);
  }
} finally {
  await dataSource.destroy().catch(console.error);
}
```

This concludes the DataSource API reference. The DataSource is the central component of Neo4j-ORM and provides the foundation for all database operations.
