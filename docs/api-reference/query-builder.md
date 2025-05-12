# QueryBuilder API Reference

The QueryBuilder provides a fluent API for building complex Cypher queries. It allows you to create highly customized queries beyond the capabilities of the Repository methods.

## Getting a QueryBuilder

```typescript
// From DataSource
const queryBuilder = dataSource.createQueryBuilder();

// From Repository
const queryBuilder = userRepository.createQueryBuilder();

// From EntityManager
const queryBuilder = entityManager.createQueryBuilder();
```

## Building Queries

The QueryBuilder uses a chain of method calls to construct a Cypher query:

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

## Node Matching Methods

### match

```typescript
match(nodeOrAlias: string | any, entityClass?: new (...args: any[]) => any): this
```

Adds a MATCH clause to the query.

**Parameters:**
- `nodeOrAlias`: Either a string (identifier) or a configuration object
- `entityClass` (optional): The entity class to match

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates a node pattern with the specified label
- Uses the entity class name as the label if not specified otherwise

**Example:**
```typescript
// Simple match with identifier and entity class
queryBuilder.match('u', User);
// Generates: MATCH (u:User)

// Match with configuration object
queryBuilder.match({
  identifier: 'u',
  label: 'User',
  where: { name: 'John' },
  optional: false
});
// Generates: MATCH (u:User {name: 'John'})

// Match with different label
queryBuilder.match({
  identifier: 'p',
  label: 'Product',
  where: { price: { [Op.gt]: 100 } }
});
// Generates: MATCH (p:Product) WHERE p.price > 100
```

### leftJoin

```typescript
leftJoin(property: string, alias: string): this
```

Adds an OPTIONAL MATCH clause for a relationship.

**Parameters:**
- `property`: The relationship property in format 'parentAlias.relationName'
- `alias`: The alias for the target node

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates an OPTIONAL MATCH for the specified relationship

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .leftJoin('u.profile', 'p');
// Generates: MATCH (u:User) OPTIONAL MATCH (u)-[:HAS_PROFILE]->(p)
```

### leftJoinAndSelect

```typescript
leftJoinAndSelect(property: string, alias: string): this
```

Adds an OPTIONAL MATCH clause and includes the result in the RETURN clause.

**Parameters:**
- `property`: The relationship property in format 'parentAlias.relationName'
- `alias`: The alias for the target node

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates an OPTIONAL MATCH and adds the target to the RETURN clause

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .leftJoinAndSelect('u.posts', 'p');
// Generates: MATCH (u:User) OPTIONAL MATCH (u)-[:HAS_POST]->(p) RETURN u, p
```

### innerJoin

```typescript
innerJoin(property: string, alias: string, condition?: string): this
```

Adds a MATCH clause for a relationship.

**Parameters:**
- `property`: The relationship property in format 'parentAlias.relationName'
- `alias`: The alias for the target node
- `condition` (optional): Additional condition for the relationship

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates a MATCH for the specified relationship

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .innerJoin('u.posts', 'p');
// Generates: MATCH (u:User) MATCH (u)-[:HAS_POST]->(p)

// With condition
queryBuilder
  .match('u', User)
  .innerJoin('u.posts', 'p', 'p.published = true');
// Generates: MATCH (u:User) MATCH (u)-[:HAS_POST]->(p) WHERE p.published = true
```

### innerJoinAndSelect

```typescript
innerJoinAndSelect(property: string, alias: string, condition?: string): this
```

Adds a MATCH clause for a relationship and includes the result in the RETURN clause.

**Parameters:**
- `property`: The relationship property in format 'parentAlias.relationName'
- `alias`: The alias for the target node
- `condition` (optional): Additional condition for the relationship

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates a MATCH and adds the target to the RETURN clause

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .innerJoinAndSelect('u.posts', 'p');
// Generates: MATCH (u:User) MATCH (u)-[:HAS_POST]->(p) RETURN u, p
```

## Filter and Condition Methods

### where

```typescript
where(condition: string | Function, parameters?: any): this
```

Adds a WHERE clause to the query.

**Parameters:**
- `condition`: A string with the condition or a function for nested conditions
- `parameters` (optional): Parameters for the condition

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Adds a WHERE clause with the specified condition
- If a function is provided, creates a nested condition

**Example:**
```typescript
// Simple string condition
queryBuilder
  .match('u', User)
  .where('u.age > 18');
// Generates: MATCH (u:User) WHERE u.age > 18

// With parameters
queryBuilder
  .match('u', User)
  .where('u.name = $name', { name: 'John' });
// Generates: MATCH (u:User) WHERE u.name = $name

// With function for nested condition
queryBuilder
  .match('u', User)
  .where(qb => {
    qb.where('u.age > 18').andWhere('u.age < 65');
  });
// Generates: MATCH (u:User) WHERE ((u.age > 18) AND (u.age < 65))
```

### andWhere

```typescript
andWhere(condition: string | Function, parameters?: any): this
```

Adds an AND condition to the WHERE clause.

**Parameters:**
- `condition`: A string with the condition or a function for nested conditions
- `parameters` (optional): Parameters for the condition

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Adds an AND condition to the existing WHERE clause
- If no WHERE clause exists yet, acts like where()

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .where('u.age > 18')
  .andWhere('u.active = true');
// Generates: MATCH (u:User) WHERE u.age > 18 AND u.active = true
```

### orWhere

```typescript
orWhere(condition: string | Function, parameters?: any): this
```

Adds an OR condition to the WHERE clause.

**Parameters:**
- `condition`: A string with the condition or a function for nested conditions
- `parameters` (optional): Parameters for the condition

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Adds an OR condition to the existing WHERE clause
- If no WHERE clause exists yet, acts like where()

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .where('u.role = "admin"')
  .orWhere('u.role = "moderator"');
// Generates: MATCH (u:User) WHERE u.role = "admin" OR u.role = "moderator"

// With nested conditions
queryBuilder
  .match('u', User)
  .where('u.role = "admin"')
  .orWhere(qb => {
    qb.where('u.role = "user"').andWhere('u.verified = true');
  });
// Generates: MATCH (u:User) WHERE u.role = "admin" OR ((u.role = "user") AND (u.verified = true))
```

## Ordering and Pagination Methods

### orderBy

```typescript
orderBy(sort: string, order: 'ASC' | 'DESC' = 'ASC'): this
```

Adds an ORDER BY clause to the query.

**Parameters:**
- `sort`: The property to sort by (can include the entity alias)
- `order` (optional): The sort direction ('ASC' or 'DESC', default is 'ASC')

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Orders the results by the specified property and direction

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .orderBy('u.lastName', 'ASC');
// Generates: MATCH (u:User) ORDER BY u.lastName ASC

// Property path format
queryBuilder
  .match('u', User)
  .orderBy('u.createdAt', 'DESC');
// Generates: MATCH (u:User) ORDER BY u.createdAt DESC
```

### skip

```typescript
skip(count: number): this
```

Adds a SKIP clause to the query.

**Parameters:**
- `count`: The number of results to skip

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Skips the specified number of results

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .skip(10);
// Generates: MATCH (u:User) SKIP 10
```

### limit

```typescript
limit(count: number): this
```

Adds a LIMIT clause to the query.

**Parameters:**
- `count`: The maximum number of results to return

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Limits the results to the specified count

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .limit(5);
// Generates: MATCH (u:User) LIMIT 5

// With skip for pagination
queryBuilder
  .match('u', User)
  .skip(20)
  .limit(10);
// Generates: MATCH (u:User) SKIP 20 LIMIT 10
```

## Return and With Methods

### return

```typescript
return(value: string): this
```

Adds a RETURN clause to the query.

**Parameters:**
- `value`: The return expression

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Specifies what to return from the query

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .return('u');
// Generates: MATCH (u:User) RETURN u

// Return specific properties
queryBuilder
  .match('u', User)
  .return('u.name, u.email');
// Generates: MATCH (u:User) RETURN u.name, u.email

// Return with aggregation
queryBuilder
  .match('u', User)
  .match({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'AUTHORED' },
      { identifier: 'p' }
    ]
  })
  .return('u.name, count(p) as postCount');
// Generates: MATCH (u:User) MATCH (u)-[:AUTHORED]->(p) RETURN u.name, count(p) as postCount
```

### with

```typescript
with(expression: string): this
```

Adds a WITH clause to the query.

**Parameters:**
- `expression`: The WITH expression

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates an intermediate result to use in subsequent parts of the query

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .with('u, size((u)-[:AUTHORED]->()) as postCount')
  .where('postCount > 3')
  .return('u');
// Generates: MATCH (u:User) WITH u, size((u)-[:AUTHORED]->()) as postCount WHERE postCount > 3 RETURN u
```

## Creation and Update Methods

### create

```typescript
create(options: any): this
```

Adds a CREATE clause to the query.

**Parameters:**
- `options`: Node creation options

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Creates a new node with the specified properties

**Example:**
```typescript
queryBuilder
  .create({
    identifier: 'u',
    label: 'User',
    properties: {
      name: 'John Doe',
      email: 'john@example.com'
    }
  });
// Generates: CREATE (u:User {name: 'John Doe', email: 'john@example.com'})
```

### set

```typescript
set(options: any): this
```

Adds a SET clause to the query.

**Parameters:**
- `options`: Node update options

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Updates the properties of a node

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .where('u.id = "123"')
  .set({
    identifier: 'u',
    properties: {
      name: 'John Smith',
      updatedAt: new Date()
    }
  });
// Generates: MATCH (u:User) WHERE u.id = "123" SET u = {name: 'John Smith', updatedAt: '2023-01-01T12:00:00.000Z'}
```

### delete

```typescript
delete(options: any): this
```

Adds a DELETE clause to the query.

**Parameters:**
- `options`: Delete options

**Returns:**
- The QueryBuilder instance for chaining

**Default behavior:**
- Deletes the specified nodes

**Example:**
```typescript
queryBuilder
  .match('u', User)
  .where('u.id = "123"')
  .delete('u');
// Generates: MATCH (u:User) WHERE u.id = "123" DELETE u

// With detach option
queryBuilder
  .match('u', User)
  .where('u.id = "123"')
  .delete({
    detach: true,
    identifiers: ['u']
  });
// Generates: MATCH (u:User) WHERE u.id = "123" DETACH DELETE u
```

## Execution Methods

### getRaw

```typescript
async getRaw(): Promise<any>
```

Executes the query and returns the raw result.

**Returns:**
- A Promise that resolves to the raw Neo4j result

**Example:**
```typescript
const result = await queryBuilder
  .match('u', User)
  .return('u')
  .getRaw();

console.log(result.records); // Raw Neo4j records
```

### getRawOne

```typescript
async getRawOne(): Promise<any>
```

Executes the query and returns the first raw result.

**Returns:**
- A Promise that resolves to the first record, or null if no results

**Default behavior:**
- Automatically adds LIMIT 1 if not already specified
- Returns null if no results are found

**Example:**
```typescript
const record = await queryBuilder
  .match('u', User)
  .where('u.email = "john@example.com"')
  .return('u')
  .getRawOne();

console.log(record ? record.get('u').properties : null);
```

### getRawMany

```typescript
async getRawMany(): Promise<any[]>
```

Executes the query and returns all raw results.

**Returns:**
- A Promise that resolves to an array of records

**Example:**
```typescript
const records = await queryBuilder
  .match('u', User)
  .return('u')
  .getRawMany();

console.log(records.map(record => record.get('u').properties));
```

### getCount

```typescript
async getCount(): Promise<number>
```

Executes the query and returns the count of results.

**Returns:**
- A Promise that resolves to the count

**Default behavior:**
- Transforms the query into a count query by replacing the RETURN clause
- If no RETURN clause exists, appends `RETURN count(*) as count`

**Example:**
```typescript
const count = await queryBuilder
  .match('u', User)
  .where('u.active = true')
  .getCount();

console.log(`Active users: ${count}`);
```

### getManyAndCount

```typescript
async getManyAndCount(): Promise<[any[], number]>
```

Executes the query and returns both the results and the count.

**Returns:**
- A Promise that resolves to a tuple containing the entities and the total count

**Default behavior:**
- Performs two queries: one for the results and one for the count

**Example:**
```typescript
const [users, count] = await queryBuilder
  .match('u', User)
  .where('u.country = "USA"')
  .orderBy('u.name', 'ASC')
  .skip(0)
  .limit(10)
  .return('u')
  .getManyAndCount();

console.log(`Users: ${users.length}, Total: ${count}`);
```

### getMany

```typescript
async getMany<T = any>(): Promise<T[]>
```

Executes the query and returns entity objects.

**Parameters:**
- `T` (type parameter): The entity type

**Returns:**
- A Promise that resolves to an array of entities

**Default behavior:**
- Converts Neo4j nodes to entity objects
- If no RETURN clause is specified, adds a generic one for the main entity

**Example:**
```typescript
const users = await queryBuilder
  .match('u', User)
  .where('u.active = true')
  .return('u')
  .getMany<User>();

console.log(users); // Array of User objects
```

### getOne

```typescript
async getOne<T = any>(): Promise<T | null>
```

Executes the query and returns a single entity object.

**Parameters:**
- `T` (type parameter): The entity type

**Returns:**
- A Promise that resolves to an entity or null if not found

**Default behavior:**
- Automatically adds LIMIT 1 if not already specified
- Returns null if no results are found
- Converts the Neo4j node to an entity object

**Example:**
```typescript
const user = await queryBuilder
  .match('u', User)
  .where('u.email = "john@example.com"')
  .return('u')
  .getOne<User>();

console.log(user ? user.name : 'User not found');
```

### execute

```typescript
async execute(): Promise<void>
```

Executes the query without returning any results.

**Returns:**
- A Promise that resolves when the query completes

**Default behavior:**
- Useful for CREATE, SET, DELETE operations where you don't need the results

**Example:**
```typescript
await queryBuilder
  .match('u', User)
  .where('u.verified = false')
  .delete('u')
  .execute();

console.log('Deleted all unverified users');
```

## Advanced QueryBuilder Patterns

### Subqueries with Functions

You can create subqueries using functions:

```typescript
queryBuilder
  .match('u', User)
  .where(qb => {
    qb.where('u.role = "admin"')
      .orWhere('u.role = "moderator"');
  })
  .andWhere(qb => {
    qb.where('u.active = true')
      .andWhere('u.verified = true');
  })
  .return('u');

// Generates:
// MATCH (u:User)
// WHERE ((u.role = "admin") OR (u.role = "moderator"))
// AND ((u.active = true) AND (u.verified = true))
// RETURN u
```

### Relationship Queries

Querying with relationships:

```typescript
queryBuilder
  .match('u', User)
  .match({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'AUTHORED', identifier: 'r' },
      { identifier: 'p', label: 'Post' }
    ]
  })
  .where('p.published = true')
  .with('u, count(p) as postCount')
  .where('postCount > 5')
  .return('u, postCount')
  .orderBy('postCount', 'DESC');

// Generates:
// MATCH (u:User)
// MATCH (u)-[r:AUTHORED]->(p:Post)
// WHERE p.published = true
// WITH u, count(p) as postCount
// WHERE postCount > 5
// RETURN u, postCount
// ORDER BY postCount DESC
```

### Path Queries

Finding paths between nodes:

```typescript
queryBuilder
  .match('u1', User)
  .where('u1.id = "user1"')
  .match('u2', User)
  .where('u2.id = "user2"')
  .with('u1, u2')
  .match('path = shortestPath((u1)-[:FOLLOWS*]-(u2))')
  .return('path, length(path) as distance');

// Generates:
// MATCH (u1:User)
// WHERE u1.id = "user1"
// MATCH (u2:User)
// WHERE u2.id = "user2"
// WITH u1, u2
// MATCH path = shortestPath((u1)-[:FOLLOWS*]-(u2))
// RETURN path, length(path) as distance
```

### Complex Aggregations

Performing aggregations and transformations:

```typescript
queryBuilder
  .match('u', User)
  .match({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'AUTHORED' },
      { identifier: 'p', label: 'Post' }
    ]
  })
  .with('u, collect(p) as posts')
  .return('u.name, size(posts) as postCount, [post in posts | post.title] as titles');

// Generates:
// MATCH (u:User)
// MATCH (u)-[:AUTHORED]->(p:Post)
// WITH u, collect(p) as posts
// RETURN u.name, size(posts) as postCount, [post in posts | post.title] as titles
```

### Creation with Relationships

Creating nodes with relationships:

```typescript
queryBuilder
  .create({
    identifier: 'u',
    label: 'User',
    properties: {
      name: 'John Doe',
      email: 'john@example.com'
    }
  })
  .create({
    identifier: 'p',
    label: 'Post',
    properties: {
      title: 'First Post',
      content: 'Hello world'
    }
  })
  .create({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'AUTHORED', properties: { createdAt: new Date() } },
      { identifier: 'p' }
    ]
  })
  .return('u, p');

// Generates:
// CREATE (u:User {name: 'John Doe', email: 'john@example.com'})
// CREATE (p:Post {title: 'First Post', content: 'Hello world'})
// CREATE (u)-[:AUTHORED {createdAt: '2023-01-01T12:00:00.000Z'}]->(p)
// RETURN u, p
```

## Using Parameters

Adding parameters to a query:

```typescript
const queryBuilder = dataSource.createQueryBuilder();

// Build the query
queryBuilder
  .match('u', User)
  .where('u.email = $email')
  .andWhere('u.active = $active')
  .return('u');

// Add parameters
queryBuilder.neogmaQueryBuilder.getBindParam().add({
  email: 'john@example.com',
  active: true
});

// Execute the query
const user = await queryBuilder.getOne<User>();
```

## Best Practices

1. **Use aliases consistently:**
   - Choose meaningful aliases for your nodes (e.g., 'u' for users, 'p' for posts)
   - Be consistent with your naming conventions

2. **Organize complex queries:**
   - Use `WITH` clauses to create intermediate results
   - Break down complex logic into smaller parts

3. **Use parameters:**
   - Always use parameters for dynamic values
   - This prevents Cypher injection attacks and improves performance

4. **Optimize your queries:**
   - Filter early to reduce the amount of data processed
   - Use appropriate indexes in your entity definitions
   - Consider using `LIMIT` for large result sets

5. **Return only what you need:**
   - Be specific in your `RETURN` clause
   - Avoid returning unnecessary data

6. **Handle transactions:**
   - For multiple write operations, use transactions
   - This ensures data consistency

## Common Issues and Solutions

### QueryBuilder with Parameters

**Problem:** Parameters are not being applied to the query.

**Solution:** Make sure to add parameters using the Neogma bind param API:

```typescript
queryBuilder
  .match('u', User)
  .where('u.email = $email');

// Correct way to add parameters
queryBuilder.neogmaQueryBuilder.getBindParam().add({ email: 'john@example.com' });

// Not with where's second parameter (which only works for simple cases)
// queryBuilder.where('u.email = $email', { email: 'john@example.com' });
```

### Type Conversion Issues

**Problem:** Results are not correctly converted to entity types.

**Solution:** Make sure your query's RETURN clause matches what the get methods expect:

```typescript
// For getMany<User>() to work properly, return the node directly
queryBuilder
  .match('u', User)
  .return('u');  // Return the whole node, not just properties

// Not like this for entity conversion
// queryBuilder.return('u.name, u.email');  // This returns only properties
```

### Performance Issues with Large Datasets

**Problem:** Queries are slow with large datasets.

**Solution:** Use pagination and optimize your query:

```typescript
// Use pagination
queryBuilder
  .match('u', User)
  .where('u.active = true')
  .orderBy('u.createdAt', 'DESC')
  .skip(offset)
  .limit(pageSize)
  .return('u');

// Filter early
queryBuilder
  .match('u', User)
  .where('u.country = "USA"')  // Filter early
  .match({
    related: [
      { identifier: 'u' },
      { direction: 'out', name: 'PURCHASED' },
      { identifier: 'p', label: 'Product' }
    ]
  });
```

This concludes the QueryBuilder API reference.