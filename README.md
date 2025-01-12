# Basler Edition der Bernoulli-Briefwechsel 

Public repository for the Basler Edition der Bernoulli-Briefwechsel data.

## Validation

Transcriptions proper are automatically validated on CI upon push. 

```shell
xmllint --noout --nowarning --relaxng resources/odd/tei_all.rng data/Edited_text/**/*.xml
```

### Registers

To validate the register files, these need to first be assembled in the `combined-index.xml` which can then be validated. 

To assemble:

```bash
$python data/Register/create-combined-index-list.py
Kombinierte Datei 'data/Register/combined-indices.xml' wurde erfolgreich erstellt.
```

To validate:

```shell
xmllint --noout --nowarning --xinclude --relaxng resources/odd/tei_all.rng data/Register/combined-indices.xml   
```
