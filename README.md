
# Simple Blockchain

This project implements a basic blockchain from scratch using Python and Flask. It simulates how blockchain technology works at a fundamental level — including mining blocks, validating proof-of-work, handling transactions, and achieving consensus across multiple nodes in a peer-to-peer network.


## Features

- Block creation with proof-of-work (PoW)

- Transaction handling between addresses

- Genesis block initialization

- SHA-256 hashing of blocks

- Node registration and peer communication

- Consensus algorithm to resolve conflicts

- Flask-based API with endpoints to interact with the blockchain


## Endpoints

#### Mine


| Endpoint | Method     | Description                |
| :-------- | :------- | :------------------------- |
| `/mine` | `Get` | Mines a new block and receives reward |

#### Transaction


| Endpoint | Method     | Description                |
| :-------- | :------- | :------------------------- |
| `/transaction/new` | `POST` | Creates a new transaction |

#### Get Chain


| Endpoint | Method     | Description                |
| :-------- | :------- | :------------------------- |
| `/chain` | `Get` | Returns the full blockchain |

#### Register Node


| Endpoint | Method     | Description                |
| :-------- | :------- | :------------------------- |
| `/nodes/register` | `POST` | Registers new nodes in the network |

#### Validate Chain


| Endpoint | Method     | Description                |
| :-------- | :------- | :------------------------- |
| `/nodes/resolve` | `Get` | Reaches consensus to ensure valid chain |

## How It Works

- Create transactions via the /transaction/new endpoint.

- Mine blocks using proof-of-work via /mine.

- Link blocks with hashes and maintain integrity.

- Share blocks across nodes and reach consensus using /nodes/resolve.
## Requirments

- Python 3

- Flask (for REST API)

- requests (for node communication)
## Acknowledgements

 - [hackernoon](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)

