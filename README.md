# Mad Maids LMS

This repository contains a simple scraper script that obtains all the material
links from the learning management system.

## Notes

If you'd like to use the `get_links.py` script to update the `.json` files,
first make sure that you have `Python` and
[`ChromeDriver`](https://sites.google.com/chromium.org/driver/downloads?authuser=0)
installed on your computer (if you are using Windows, make sure to move the
`chromedriver.exe` to the working directory). Then, create and activate a
virtual environment and install the required packages with the following
command:

```shell
python3 -m pip install -r requirements.txt
```

Finally, change the variables in the `.env.example` file and rename it to
`.env`. Run the script with the following command:

```shell
python3 get_jsons.py
```

---

> The project is being actively edited in order to keep the latest information,
> if you found our information outdated, please
> [open issues](https://github.com/mad-maids/maid.lms/issues/new) and let us
> know about it.

<p align="center">Copyright &copy; 2021 <a href="https://maid.uz" target="_blank">Mad Maids</a></p>

<p align="center"><a href="https://github.com/mad-maids/maid.lms/blob/master/license"><img src="https://img.shields.io/static/v1.svg?style=flat-square&label=License&message=MIT&logoColor=eceff4&logo=github&colorA=000000&colorB=ffffff"/></a></p>
