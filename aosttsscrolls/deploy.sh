#!/bin/bash
gcloud run deploy aosttsscrolls --image gcr.io/oneoff-project/aosttsscrolls:latest --allow-unauthenticated --platform managed --region us-central1
