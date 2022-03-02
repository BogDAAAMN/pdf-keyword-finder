# pdf-keyword-finder

Tiny python script to find keywords in a collection of PDF files.

## Usage

```bash
$ git clone https://github.com/maastrichtlawtech/pdf-keyword-finder
```

```
usage: find.py src keywords [out]

Find keywords in a collection of PDF files.

positional arguments:
  src         source directory with PDF files
  keywords    list of keyword separated by comma
  out         name of the output xlsx file

optional arguments:
  -h, --help  show this help message and exit
```

## Examples

- List of keywords 
  ```bash
  $ python3 find.py "./data/" "referral jurisdiction, Article 214 RTC"
  ```
- Single keyword
  ```bash
  $ python3 find.py "./data/" "referral"
  ```
- Custom out file name
    ```bash
  $ python3 find.py "./data/" "referral jurisdiction, Article 214 RTC" "data-02-march.xlsx"
  ```
