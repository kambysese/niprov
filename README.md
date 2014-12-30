niprov
======
provenance for neuroimaging data

[![Build Status](https://travis-ci.org/ilogue/niprov.svg?branch=master)](https://travis-ci.org/ilogue/niprov)

To inspect image files, install `nibabel` and/or `pydicom`.

Commandline Usage
-----------------

```
discover .
```
*Look for image files below the current directory, inspect them and store the obtained provenance metadata.*

```
provenance --subject "John Doe"
```
*Show provenance of known files for subject 'John Doe'.*

Python Usage
-----------------

```
import niprov
niprov.discover('.')
files = niprov.report(forSubject='John Doe')
```


