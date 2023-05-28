# RDM_calculation
This repo is the code needed to calculate the RDM index

## About RDM index
The purpose of the RDM index is to quantitatively assess how suitable a site is to Lotus Project's Rural Development Model (RDM) framework

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [python](https://www.python.org)
* [pandas](https://pandas.pydata.org)
* [numpy](https://numpy.org/)
* [rasterio](https://rasterio.readthedocs.io/en/latest/)

<p align="right">(<a href="#top">back to top</a>)</p>

### Repo Structure

```
.
├── RDM_example.ipynb --------> the notebook giving an example of how to calculate the RDM index
├── RDM_main.py -------> main code used to calculate RDM index
├── TIF_loading
|   └── TIF_Transform.py -------> modules used to load tifs and transform them
|   └── maskTIF.py --------> module used to mask tifs
├── AutoScale
|   └── AutoScale.py -------> module used to autoscale tifs according scales present in data
├── README.md
├── LICENSE
└── requirements.txt

```
<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* python 3.9
  ```sh
  https://www.python.org/downloads/
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/lotus-project/anapp.git
   ```
3. Install packages/libraries
   ```sh
    conda env create -f environment.yml
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

### Run the App

See RDM_example.ipynb for more info

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [] Feature 1
- [] Feature 2
- [] Feature 3
    - [] Nested Feature

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the LP community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'Add some NewFeature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.


<!-- CONTACT -->
## Contact

Anshul Verma - anshul@lotus-project.org

Project Link: [https://github.com/lotus-project/RDM_calculation](https://github.com/lotus-project/RDM_calculation)

<p align="right">(<a href="#top">back to top</a>)</p>

