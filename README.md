# Neode Documentation

## Introduction

Neode is a powerful Neo4j Object Graph Mapper (OGM) for Node.js. It provides a simple and intuitive interface for interacting with Neo4j graph databases, making it easy to define models, create relationships, and query your graph data.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
  - [Basic Connection](#basic-connection)
  - [Environment Variables](#environment-variables)
- [Models](#models)
  - [Defining Models](#defining-models)
  - [Properties](#properties)
  - [Relationships](#relationships)
  - [Loading Models](#loading-models)
  - [Extending Models](#extending-models)
- [CRUD Operations](#crud-operations)
  - [Creating Nodes](#creating-nodes)
  - [Reading Nodes](#reading-nodes)
  - [Updating Nodes](#updating-nodes)
  - [Deleting Nodes](#deleting-nodes)
- [Relationships](#relationships-1)
  - [Creating Relationships](#creating-relationships)
  - [Relationship Properties](#relationship-properties)
  - [Querying Relationships](#querying-relationships)
- [Querying](#querying)
  - [Basic Queries](#basic-queries)
  - [Query Builder](#query-builder)
  - [Raw Cypher](#raw-cypher)
- [Transactions](#transactions)
- [Batch Operations](#batch-operations)
- [Schema Management](#schema-management)
- [Advanced Features](#advanced-features)
  - [Collections](#collections)
  - [Eager Loading](#eager-loading)
  - [Data Types](#data-types)
  - [Validation](#validation)

## Installation

Install Neode using npm:

```bash
npm install neode
```

## Configuration

### Basic Connection

```javascript
const Neode = require('neode');

// Connect to the database
const neode = new Neode(
  'bolt://localhost:7687',    // Connection string
  'username',                 // Username
  'password',                 // Password
  false,                      // Enterprise edition? (boolean)
  'neo4j',                    // Database name (defaults to 'neo4j')
  {                           // Additional driver configuration
    // Neo4j driver configuration options
  }
);
```

### Environment Variables

You can also configure Neode using environment variables in a `.env` file:

```
NEO4J_PROTOCOL=bolt
NEO4J_HOST=localhost
NEO4J_PORT=7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
NEO4J_ENTERPRISE=false

# Optional additional configuration
NEO4J_ENCRYPTION=ENCRYPTION_OFF
NEO4J_TRUST=TRUST_ALL_CERTIFICATES
NEO4J_TRUSTED_CERTIFICATES=certificates.pem
NEO4J_KNOWN_HOSTS=known_hosts
NEO4J_MAX_CONNECTION_POOLSIZE=100
NEO4J_MAX_TRANSACTION_RETRY_TIME=5000
NEO4J_LOAD_BALANCING_STRATEGY=LEAST_CONNECTED
NEO4J_MAX_CONNECTION_LIFETIME=3600000
NEO4J_CONNECTION_TIMEOUT=30000
NEO4J_DISABLE_LOSSLESS_INTEGERS=true
NEO4J_LOGGING_LEVEL=info
```

Then create the Neode instance:

```javascript
const neode = require('neode').fromEnv();
```

## Models

### Defining Models

Models define the structure of your nodes in the graph. Each model represents a label in Neo4j.

```javascript
const personSchema = {
  // Basic properties
  person_id: {
    type: 'uuid',
    primary: true
  },
  name: {
    type: 'string',
    required: true,
    index: true
  },
  age: {
    type: 'number',
    min: 0,
    max: 120,
    integer: true
  },
  active: {
    type: 'boolean',
    default: true
  },
  
  // Relationships
  friends: {
    type: 'relationships',
    relationship: 'FRIENDS_WITH',
    direction: 'BOTH',
    target: 'Person',
    properties: {
      since: {
        type: 'date',
        default: () => new Date()
      }
    },
    eager: true
  },
  posts: {
    type: 'nodes',
    relationship: 'CREATED',
    direction: 'OUT',
    target: 'Post',
    cascade: 'delete'
  }
};

// Define the model
neode.model('Person', personSchema);
```

### Properties

Property types supported by Neode:

| Type | Description |
|------|-------------|
| `string` | String values |
| `number` | Number values (float) |
| `int` or `integer` | Integer values |
| `boolean` | Boolean values |
| `uuid` | Auto-generates a UUID when created |
| `date` | Neo4j Date type |
| `datetime` | Neo4j DateTime type |
| `time` | Neo4j Time type |
| `localtime` | Neo4j LocalTime type |
| `localdatetime` | Neo4j LocalDateTime type |
| `point` | Neo4j Point (spatial) type |

Property modifiers:

| Option | Description |
|--------|-------------|
| `primary` | Marks the property as the primary key |
| `required` | Marks the property as required |
| `unique` | Creates a unique constraint on this property |
| `index` | Creates an index on this property |
| `default` | Default value or function to generate one |
| `min` | Minimum value for number properties |
| `max` | Maximum value for number properties |
| `regex` | Regular expression to validate string properties |
| `email` | Validates as an email address |
| `hidden` | Hides the property from JSON output |
| `readonly` | Property can be read but not written back to database |
| `protected` | Property can only be set on creation |

### Relationships

Relationship types:

| Type | Description |
|------|-------------|
| `relationship` | Single relationship to one node |
| `relationships` | Collection of relationships to multiple nodes |
| `node` | Single related node |
| `nodes` | Collection of related nodes |

Relationship direction options:

| Direction | Constant | Description |
|-----------|----------|-------------|
| `IN` | `DIRECTION_IN` | Relationship points to this node |
| `OUT` | `DIRECTION_OUT` | Relationship points from this node to target |
| `BOTH` | `DIRECTION_BOTH` | Bidirectional relationship |

### Loading Models

You can load multiple models at once:

```javascript
// Load multiple models
neode.with({
  Person: personSchema,
  Post: postSchema,
  Comment: commentSchema
});

// Load models from a directory
neode.withDirectory('./models');
```

### Extending Models

Extend a model to create a new model that inherits properties from the parent:

```javascript
neode.extend('Person', 'Employee', {
  // Additional properties for employees
  employee_id: {
    type: 'string',
    required: true,
    unique: true
  },
  department: {
    type: 'string'
  }
});
```

## CRUD Operations

### Creating Nodes

```javascript
// Create a single node
neode.create('Person', {
  name: 'Alice',
  age: 32
})
  .then(alice => {
    console.log(alice.toJson());
  });

// Merge a node (create if it doesn't exist)
neode.merge('Person', {
  person_id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'Bob',
  age: 30
})
  .then(bob => {
    console.log(bob.toJson());
  });

// Merge with specific fields
neode.mergeOn('Person', 
  { email: 'charlie@example.com' }, // Match criteria
  { name: 'Charlie', age: 45 }      // Properties to set
)
  .then(charlie => {
    console.log(charlie.toJson());
  });
```

### Reading Nodes

```javascript
// Find by primary key
neode.find('Person', 'person_id_value')
  .then(person => {
    console.log(person.toJson());
  });

// Find by internal Neo4j ID
neode.findById('Person', 123)
  .then(person => {
    console.log(person.toJson());
  });

// Find by properties
neode.first('Person', 'name', 'Alice')
  .then(alice => {
    console.log(alice.toJson());
  });

// Find by multiple properties
neode.first('Person', { name: 'Alice', age: 32 })
  .then(alice => {
    console.log(alice.toJson());
  });

// Get all nodes with a label
neode.all('Person')
  .then(people => {
    people.forEach(person => {
      console.log(person.toJson());
    });
  });

// Get all with properties and pagination
neode.all('Person', 
  { active: true },   // Properties
  'name',             // Order by
  10,                 // Limit
  0                   // Skip
)
  .then(people => {
    // Collection of people
  });

// Find nodes within a certain distance (spatial query)
neode.withDistance(
  'Person',
  'location',          // Location property
  { latitude: 51.5074, longitude: -0.1278 }, // Point
  5000,                // Distance in meters
  { active: true },    // Additional properties
  'name',              // Order by
  10,                  // Limit
  0                    // Skip
)
  .then(people => {
    // Collection of people within 5km
  });
```

### Updating Nodes

```javascript
// First find the node
neode.find('Person', 'person_id_value')
  .then(person => {
    // Then update it
    return person.update({
      age: 33,
      name: 'Alice Smith'
    });
  })
  .then(person => {
    console.log('Person updated', person.toJson());
  });
```

### Deleting Nodes

```javascript
// Delete a single node
neode.find('Person', 'person_id_value')
  .then(person => {
    return person.delete();
  })
  .then(() => {
    console.log('Person deleted');
  });

// Delete with cascade (specified depth)
neode.find('Person', 'person_id_value')
  .then(person => {
    return person.delete(2); // Delete with depth of 2
  });

// Delete all nodes with a label
neode.deleteAll('Person')
  .then(() => {
    console.log('All people deleted');
  });
```

## Relationships

### Creating Relationships

```javascript
// First get the nodes
Promise.all([
  neode.find('Person', 'alice_id'),
  neode.find('Person', 'bob_id')
])
  .then(([alice, bob]) => {
    // Create relationship
    return alice.relateTo(bob, 'friends', { since: new Date() });
  })
  .then(relationship => {
    console.log('Relationship created', relationship.toJson());
  });

// Alternative using relate method
Promise.all([
  neode.find('Person', 'alice_id'),
  neode.find('Person', 'bob_id')
])
  .then(([alice, bob]) => {
    return neode.relate(alice, bob, 'friends', { since: new Date() });
  });

// Create with force_create=true to always create a new relationship
// instead of merging
alice.relateTo(bob, 'friends', { since: new Date() }, true);
```

### Relationship Properties

```javascript
// Update relationship properties
relationship.update({
  since: new Date('2020-01-01'),
  strength: 5
})
  .then(updated => {
    console.log('Relationship updated', updated.toJson());
  });
```

### Querying Relationships

```javascript
// When eager loading is enabled, relationships are loaded automatically
neode.find('Person', 'alice_id')
  .then(alice => {
    // Get friends relationship
    return alice.get('friends').toJson();
  })
  .then(friends => {
    console.log(friends);
  });

// Removing relationships
alice.detachFrom(bob)
  .then(() => {
    console.log('Relationship deleted');
  });

// Delete a specific relationship
relationship.delete()
  .then(() => {
    console.log('Relationship deleted');
  });
```

## Querying

### Basic Queries

```javascript
// Simple find methods
neode.find('Person', 'id');
neode.first('Person', 'email', 'alice@example.com');
neode.all('Person', { active: true });
```

### Query Builder

Neode includes a fluent query builder for more complex queries:

```javascript
const builder = neode.query();

builder
  .match('person', 'Person')
  .where('person.active', true)
  .relationship('FRIENDS_WITH', 'OUT', 'friend_rel')
  .to('friend', 'Person')
  .whereRaw('friend.age > 30')
  .return('person', 'collect(friend) as friends')
  .execute()
  .then(res => {
    const people = neode.hydrate(res, 'person');
    console.log(people.toJson());
  });
```

Complex query example:

```javascript
neode.query()
  .match('person', 'Person')
  .where('person.name', 'Alice')
  .relationship('CREATED', 'OUT', 'created_rel')
  .to('post', 'Post')
  .relationship('COMMENTED_ON', 'IN', 'comment_rel')
  .to('comment', 'Comment')
  .with('person', 'post', 'collect(comment) as comments')
  .orderBy('post.created', 'DESC')
  .limit(10)
  .return('person', 'collect({post: post, comments: comments}) as activity')
  .execute()
  .then(res => {
    // Process results
  });
```

### Raw Cypher

For full control, you can run raw Cypher queries:

```javascript
// Read query
neode.readCypher(
  'MATCH (p:Person) WHERE p.name = $name RETURN p',
  { name: 'Alice' }
)
  .then(res => {
    const person = neode.hydrateFirst(res, 'p');
    console.log(person.toJson());
  });

// Write query
neode.writeCypher(
  'MATCH (p:Person {name: $name}) SET p.lastSeen = $now RETURN p',
  { name: 'Alice', now: new Date().toISOString() }
)
  .then(res => {
    const person = neode.hydrateFirst(res, 'p');
    console.log(person.toJson());
  });
```

## Transactions

```javascript
// Create a transaction
const tx = neode.transaction();

// Run queries in the transaction
tx.run('MATCH (p:Person) WHERE p.name = $name RETURN p', { name: 'Alice' })
  .then(res => {
    // Process first result
    
    // Run another query
    return tx.run(
      'MATCH (p:Person) WHERE p.name = $name SET p.visits = p.visits + 1 RETURN p',
      { name: 'Alice' }
    );
  })
  .then(res => {
    // Process second result
    
    // Commit the transaction
    return tx.success();
  })
  .then(() => {
    console.log('Transaction complete');
  })
  .catch(error => {
    // Transaction automatically rolled back on error
    console.error('Transaction failed', error);
  });
```

## Batch Operations

Run multiple queries in a single transaction:

```javascript
const queries = [
  {
    query: 'MATCH (p:Person) WHERE p.name = $name RETURN p',
    params: { name: 'Alice' }
  },
  {
    query: 'MATCH (p:Person) WHERE p.name = $name RETURN p',
    params: { name: 'Bob' }
  },
  'MATCH (p:Person) RETURN count(p) as count'
];

neode.batch(queries)
  .then(results => {
    // Array of results for each query
    console.log(results[0]); // Alice
    console.log(results[1]); // Bob
    console.log(results[2].records[0].get('count').toNumber()); // Count
  })
  .catch(error => {
    // If any query fails, the entire transaction is rolled back
    console.error('Batch failed', error);
  });
```

## Schema Management

Create constraints and indexes based on your model definitions:

```javascript
// Install constraints and indexes
neode.schema.install()
  .then(() => {
    console.log('Schema installed');
  });

// Drop all constraints and indexes
neode.schema.drop()
  .then(() => {
    console.log('Schema dropped');
  });
```

## Advanced Features

### Collections

Neode provides a Collection class to work with multiple nodes:

```javascript
// Get a collection
neode.all('Person')
  .then(people => {
    // Get length
    console.log(people.length);
    
    // Get first node
    const first = people.first();
    
    // Get by index
    const third = people.get(2);
    
    // Map over collection
    const names = people.map(person => person.get('name'));
    
    // Find in collection
    const alice = people.find(person => person.get('name') === 'Alice');
    
    // ForEach
    people.forEach(person => {
      console.log(person.get('name'));
    });
    
    // Convert all to JSON
    return people.toJson();
  })
  .then(json => {
    console.log(json);
  });
```

### Eager Loading

Enable eager loading to automatically load relationships:

```javascript
const postSchema = {
  // Properties...
  
  // Define eager loaded relationships
  author: {
    type: 'node',
    relationship: 'CREATED_BY',
    direction: 'OUT',
    target: 'Person',
    eager: true
  },
  comments: {
    type: 'nodes',
    relationship: 'HAS_COMMENT',
    direction: 'OUT',
    target: 'Comment',
    eager: true
  }
};

// Then when you retrieve a post, the author and comments are loaded automatically
neode.find('Post', 'post_id')
  .then(post => {
    // Author and comments are already loaded
    console.log(post.get('author').get('name'));
    console.log(post.get('comments').length);
    
    // Convert to JSON with eager-loaded relationships
    return post.toJson();
  })
  .then(json => {
    console.log(json);
    // {
    //   _id: 123,
    //   title: 'My Post',
    //   content: '...',
    //   author: {
    //     _id: 456,
    //     name: 'Alice'
    //   },
    //   comments: [
    //     { _id: 789, content: 'Great post!' },
    //     { _id: 790, content: 'Thanks for sharing' }
    //   ]
    // }
  });
```

### Data Types

Neode supports all Neo4j data types including:

- Temporal types: Date, DateTime, LocalDateTime, Time, LocalTime
- Spatial types: Point (2D and 3D, Cartesian and WGS84)
- Numeric types: Float, Integer (with lossless integer support)

```javascript
// Neo4j data types example
neode.create('Location', {
  name: 'London',
  coordinates: {
    latitude: 51.5074,
    longitude: -0.1278
  },
  created: new Date(),
  updated: new Date(),
  population: 8900000  // Will be converted to Neo4j Integer
})
  .then(location => {
    console.log(location.toJson());
  });
```

### Validation

Neode uses Joi for validation with custom extensions for Neo4j types:

```javascript
const schema = {
  email: {
    type: 'string',
    required: true,
    email: true,
    unique: true
  },
  age: {
    type: 'integer',
    min: 18,
    max: 100
  },
  username: {
    type: 'string',
    required: true,
    min: 3,
    max: 20,
    regex: /^[a-zA-Z0-9_]+$/
  },
  website: {
    type: 'string',
    uri: true,
    optional: true
  },
  created: {
    type: 'datetime',
    default: () => new Date()
  }
};

// Validation is automatic on create and update
neode.create('User', {
  email: 'invalid-email',
  age: 15,
  username: 'a'
})
  .catch(error => {
    // ValidationError with details about what failed
    console.error(error.details);
  });
```

## Closing the Connection

Always close the connection when your application exits:

```javascript
neode.close();
```

---

## Example Application

Here's a complete example that demonstrates several Neode features:

```javascript
const Neode = require('neode');

// Initialize Neode with connection details
const neode = new Neode(
  'bolt://localhost:7687',
  'neo4j',
  'password'
);

// Define models
neode.with({
  Person: {
    person_id: {
      type: 'uuid',
      primary: true
    },
    name: {
      type: 'string',
      required: true,
      index: true
    },
    email: {
      type: 'string',
      unique: true,
      required: true,
      email: true
    },
    age: {
      type: 'integer',
      min: 0,
      max: 120
    },
    active: {
      type: 'boolean',
      default: true
    },
    created: {
      type: 'datetime',
      default: () => new Date()
    },
    // Relationships
    friends: {
      type: 'relationships',
      relationship: 'FRIENDS_WITH',
      direction: 'BOTH',
      target: 'Person',
      properties: {
        since: {
          type: 'date',
          default: () => new Date()
        }
      },
      eager: true
    },
    posts: {
      type: 'nodes',
      relationship: 'CREATED',
      direction: 'OUT',
      target: 'Post',
      cascade: 'delete'
    }
  },
  Post: {
    post_id: {
      type: 'uuid',
      primary: true
    },
    title: {
      type: 'string',
      required: true
    },
    content: 'string',
    created: {
      type: 'datetime',
      default: () => new Date()
    },
    author: {
      type: 'node',
      relationship: 'CREATED',
      direction: 'IN',
      target: 'Person',
      eager: true
    },
    comments: {
      type: 'nodes',
      relationship: 'HAS_COMMENT',
      direction: 'OUT',
      target: 'Comment',
      eager: true,
      cascade: 'delete'
    }
  },
  Comment: {
    comment_id: {
      type: 'uuid',
      primary: true
    },
    content: {
      type: 'string',
      required: true
    },
    created: {
      type: 'datetime',
      default: () => new Date()
    },
    author: {
      type: 'node',
      relationship: 'CREATED',
      direction: 'IN',
      target: 'Person',
      eager: true
    }
  }
});

// Install schema (constraints and indexes)
neode.schema.install()
  .then(() => {
    console.log('Schema installed');
    
    // Create some people
    return Promise.all([
      neode.create('Person', {
        name: 'Alice',
        email: 'alice@example.com',
        age: 32
      }),
      neode.create('Person', {
        name: 'Bob',
        email: 'bob@example.com',
        age: 30
      })
    ]);
  })
  .then(([alice, bob]) => {
    console.
