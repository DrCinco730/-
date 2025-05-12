# Getting Started with Neo4j-ORM

This guide will help you set up Neo4j-ORM and create your first application.

## Installation

First, install the required packages:

```bash
npm install neo4j-orm neo4j-driver reflect-metadata
```

Or using yarn:

```bash
yarn add neo4j-orm neo4j-driver reflect-metadata
```

## Basic Setup

Create a new file (e.g., `index.ts`) and add the following code:

```typescript
import { DataSource, Entity, NodeId, Property } from 'neo4j-orm';
import 'reflect-metadata';

// 1. Define an entity class
@Entity()
class User {
  @NodeId({ generated: true })
  id: string;

  @Property()
  name: string;

  @Property({ unique: true })
  email: string;
}

// 2. Configure the data source
const dataSource = new DataSource({
  type: 'neo4j',
  host: 'localhost',  // Your Neo4j host
  port: 7687,         // Neo4j bolt port
  username: 'neo4j',  // Database username
  password: 'password', // Database password
  database: 'neo4j',  // Database name
  entities: [User],   // Entity classes
  synchronize: true   // Automatically create constraints and indices
});

// 3. Create the main function
async function main() {
  try {
    // Initialize the connection
    await dataSource.initialize();
    console.log('Connected to Neo4j database');

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

    // Find a specific user
    const john = await userRepository.findOne({
      where: { email: 'john@example.com' }
    });
    console.log('Found user:', john);

    // Update the user
    if (john) {
      john.name = 'John Smith';
      await userRepository.save(john);
      console.log('User updated');
    }

    // Find by ID
    if (john) {
      const userById = await userRepository.findOneById(john.id);
      console.log('User found by ID:', userById);
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Always close the connection when done
    await dataSource.destroy();
    console.log('Connection closed');
  }
}

// 4. Run the application
main().catch(console.error);
```

## Understanding the Code

1. **Import Dependencies**: Import the necessary classes from `neo4j-orm` and `reflect-metadata`.

2. **Define an Entity**: Use the `@Entity()` decorator to mark a class as a Neo4j node. Properties are defined using decorators:
   - `@NodeId()`: Marks a property as the primary identifier
   - `@Property()`: Marks a regular property to be stored in the database

3. **Configure the DataSource**: Create a `DataSource` instance with connection details and entity classes.

4. **Connect to the Database**: Call `dataSource.initialize()` to establish the connection.

5. **Get the Repository**: Use `dataSource.getRepository(Entity)` to get a repository for your entity.

6. **Perform CRUD Operations**:
   - Create: `repository.create()` and `repository.save()`
   - Read: `repository.find()`, `repository.findOne()`, `repository.findOneById()`
   - Update: Modify the entity and call `repository.save()`
   - Delete: `repository.remove()`

7. **Close the Connection**: Always call `dataSource.destroy()` when done to close the connection.

## TypeScript Configuration

Create a `tsconfig.json` file with the following content:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "strict": true,
    "outDir": "./dist",
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

Make sure to enable `experimentalDecorators` and `emitDecoratorMetadata` which are required for the decorators to work properly.

## Running the Application

Build and run your TypeScript application:

```bash
# Compile TypeScript
npx tsc

# Run the compiled JavaScript
node dist/index.js
```

## Next Steps

Now that you have a basic application working, you can explore more advanced features:

- [Core Concepts](./core-concepts.md) - Learn about the essential components of Neo4j-ORM
- [Entity Decorators](./api-reference/entity-decorators.md) - Explore all available entity decorators
- [Relationships](./examples/relationships.md) - Learn how to define and work with relationships
- [QueryBuilder](./api-reference/query-builder.md) - Build more complex queries
- [Transactions](./examples/transactions.md) - Manage database transactions
