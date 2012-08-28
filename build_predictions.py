#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "as2.settings")
    from recommendation.recengine import *
  
    print("Building prediction server\n")
    build_recommendations_by_topic()
    print("Prediction server built\n")

