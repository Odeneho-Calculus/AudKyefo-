# AudKyɛfo Tests

This directory contains test files for the AudKyɛfo application.

## Running Tests

To run all tests:

```
pytest
```

To run a specific test file:

```
pytest tests/test_helpers.py
```

## Sample Audio

The `sample_audio` directory contains audio files for testing. These files are not included in the repository due to their size, but can be generated using the `generate_sample_audio.py` script:

```
python tests/generate_sample_audio.py
```

This will create several test audio files in different formats that can be used for testing the application.