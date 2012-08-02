#!/usr/bin/env python
from recommendation.views import build_pred_server
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "as2.settings")
  
    print("Building prediction server\n")
    build_pred_server()
    print("Prediction server built\n")

