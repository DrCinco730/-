# Neo4j-ORM

Neo4j-ORM is a TypeScript/JavaScript Object-Relational Mapping (ORM) library for Neo4j graph databases. It provides a familiar API inspired by TypeORM to make working with graph databases more accessible to developers.

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

## Quick Start

```typescript
import { DataSource, Entity, NodeId, Property } from 'neo4j-orm';
import 'reflect-metadata';

// Define an entity
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property()
  name: string;

  @Property()
  email: string;
}

// Create and initialize a data source
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',
  port: 7687,
  username: 'neo4j',
  password: 'password',
  database: 'neo4j',
  entities: [User]
});

async function main() {
  // Connect to the database
  await dataSource.initialize();

  // Get the User repository
  const userRepository = dataSource.getRepository(User);

  // Create a new user
  const user = userRepository.create({
    name: 'John Doe',
    email: 'john@example.com'
  });

  // Save the user to the database
  await userRepository.save(user);
  console.log('User saved:', user);

  // Find all users
  const users = await userRepository.find();
  console.log('All users:', users);

  // Close the connection
  await dataSource.destroy();
}

main().catch(console.error);
```

## Documentation Structure

The documentation is organized into several files to make it easier to navigate:

- **[Getting Started](./docs/getting-started.md)** - Installation and basic setup
- **[Core Concepts](./docs/core-concepts.md)** - Essential concepts and components
- **[API Reference](./docs/api-reference/index.md)** - Detailed API documentation
  - [DataSource](./docs/api-reference/data-source.md)
  - [Entity Decorators](./docs/api-reference/entity-decorators.md)
  - [Property Decorators](./docs/api-reference/property-decorators.md)
  - [Relationship Decorators](./docs/api-reference/relationship-decorators.md)
  - [Repository](./docs/api-reference/repository.md)
  - [QueryBuilder](./docs/api-reference/query-builder.md)
  - [EntityManager](./docs/api-reference/entity-manager.md)
  - [Events and Subscribers](./docs/api-reference/events-subscribers.md)
  - [Utilities](./docs/api-reference/utilities.md)
- **[Examples](./docs/examples/index.md)** - Practical examples and use cases
  - [Basic CRUD Operations](./docs/examples/basic-crud.md)
  - [Relationships](./docs/examples/relationships.md)
  - [Advanced Queries](./docs/examples/advanced-queries.md)
  - [Transactions](./docs/examples/transactions.md)
  - [Event Subscribers](./docs/examples/event-subscribers.md)
  - [Migrations](./docs/examples/migrations.md)
- **[Best Practices](./docs/best-practices.md)** - Tips for optimal usage

## Features

- **TypeScript Support** - Full TypeScript integration with strong typing
- **Entity Decorators** - Define your data model using decorators
- **Graph Relationships** - First-class support for Neo4j relationships
- **Repository Pattern** - Familiar repository API for entity operations
- **Query Builder** - Fluent API for building complex Cypher queries
- **Transactions** - Support for database transactions
- **Events System** - Entity lifecycle hooks and event subscribers
- **Migrations** - Tools for managing database schema changes
- **Custom Queries** - Execute raw Cypher queries when needed

## License

[MIT](LICENSE)
