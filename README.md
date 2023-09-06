# PyCADCAR
## Python-based CAD and CAR Records

### Description
This repository provides an example IOC (Input/Output Controller) with Apply and CAD (Command Action Directive) and CAR (Command Action Response) records. The project is intended to implement the functionality of these records using Python and the caproto library.

### Features
- CAD and CAR record implementation
- Example IOC script to demonstrate functionality
- Helper tools for CA (Channel Access)

### Requirements
- Python 3.8 or higher
- caproto

### Installation
Clone the repository and navigate to its root directory. Run:

```bash
pip install .
```

### Usage

1. **Run the example IOC:**

    ```bash
    python examples/exampleIOC.py --list-pvs
    ```

2. **Execute Channel Access commands using tools:**

    ```bash
    ./tools/caget <PV_NAME>
    ./tools/caput <PV_NAME> <VALUE>
    ```


### Structure
- `examples/`: Contains example IOC Python script
- `pygeminirec/`: Main Python package containing CAD and CAR records
- `tools/`: Helper scripts for Channel Access operations

### Contributing
Feel free to submit issues or pull requests.

### License
Your preferred license here.
