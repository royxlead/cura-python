#!/usr/bin/env python3
"""
Google ALTS Warning Suppressor
This script suppresses ALTS credential warnings when using Gemini API outside GCP
"""

import os
import sys

def suppress_google_warnings():
    """Set environment variables to suppress Google ALTS warnings"""
    
    # Suppress GRPC and Google logging warnings
    warning_suppressors = {
        'GRPC_VERBOSITY': 'ERROR',
        'GLOG_minloglevel': '2',
        'GRPC_TRACE': '',
        'GOOGLE_APPLICATION_CREDENTIALS': '',
    }
    
    print("🔧 Suppressing Google ALTS and GRPC warnings...")
    
    for key, value in warning_suppressors.items():
        os.environ[key] = value
        print(f"   ✓ Set {key}={value}")
    
    print("✅ Warning suppression configured successfully!")
    print("   This will suppress the following warnings:")
    print("   - ALTS creds ignored. Not running on GCP")
    print("   - GRPC verbosity messages")
    print("   - Google logging messages below ERROR level")
    print()

if __name__ == "__main__":
    suppress_google_warnings()