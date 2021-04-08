from jsonschema import validators, Draft7Validator, FormatChecker


def validate_doc(document, company, logger):
    schema = {"$schema": "http://json-schema.org/draft-07/schema#",
              "title": "FAQ.json",
              "type": "object",
              "properties": {
                  "answer": {
                      "$ref": "#/definitions/non-empty-string"
                  },
                  "raw_question": {
                      "$ref": "#/definitions/non-empty-string",
                  },
                  "company": {
                      "const": company
                  },
                  "category": {
                      "$ref": "#/definitions/non-empty-string",
                  },
                  "html_url": {
                      "format": "uri",
                      "pattern": "^https?://(www\\.)?[a-z0-9.-]*\\.[a-z]{2,}([^>%\\x20\\x00-\\x1f\\x7F]|%[0-9a-fA-F]{2})*$"

                  },
                  "question": {
                      "type": ["string", "null"]

                  },
                  "text": {
                      "type": ["string", "null"]

                  }

              },
              "required": ["answer", "raw_question", "company", "category", "html_url", "question", "text"],
              "definitions": {
                  "non-empty-string": {
                      "type": "string",
                      "minLength": 2,
                      "pattern": r"(\S){2,}"
                  },
              }
              }

    all_validators = dict(Draft7Validator.VALIDATORS)
    Validator = validators.create(
        meta_schema=Draft7Validator.META_SCHEMA, validators=all_validators
    )
    format_checker = FormatChecker()
    FAQ_validator = Validator(
        schema, format_checker=format_checker
    )

    errors = sorted(FAQ_validator.iter_errors(document), key=lambda x: x.path)
    if len(errors) > 0:
        for error in errors:
            logger.error('%(path)s - %(error)s', {'path': str(list(error.schema_path)), 'error': error.message})
        return False
    return True
