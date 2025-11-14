#!/usr/bin/env python3
"""
Test script for the LLM text filter.

Run this to verify the text filter is working correctly before using it in production.
"""

from text_filter import LLMTextFilter


def test_text_filter():
    """Test the text filter with various inputs."""
    
    filter = LLMTextFilter()
    
    test_cases = [
        # (input, expected_output, description)
        (
            "I'm *really* excited to help!",
            "I'm really excited to help!",
            "Remove italic asterisks"
        ),
        (
            "This is **very** important!",
            "This is very important!",
            "Remove bold asterisks"
        ),
        (
            "*smiles* Sure, I can help with that!",
            "smiles Sure, I can help with that!",
            "Remove action asterisks"
        ),
        (
            "Here's the __important__ part.",
            "Here's the important part.",
            "Remove underscores"
        ),
        (
            "Check out this ~~mistake~~ correction.",
            "Check out this correction.",
            "Remove strikethrough"
        ),
        (
            "# Welcome to our service",
            "Welcome to our service",
            "Remove markdown header"
        ),
        (
            "Use the `code` function here.",
            "Use the code function here.",
            "Remove inline code backticks"
        ),
        (
            "Visit [our website](https://example.com) for more.",
            "Visit our website for more.",
            "Remove markdown links"
        ),
        (
            "This   has    multiple     spaces.",
            "This has multiple spaces.",
            "Normalize whitespace"
        ),
        (
            "Normal text without formatting.",
            "Normal text without formatting.",
            "Pass through normal text"
        ),
        (
            "**Bold** and *italic* and __underline__ all together!",
            "Bold and italic and underline all together!",
            "Multiple formatting types"
        ),
        (
            "*laughs* That's **really** funny! *winks*",
            "laughs That's really funny! winks",
            "Mixed actions and emphasis"
        ),
        (
            " your",
            " your",
            "Preserve leading space (streaming token)"
        ),
        (
            " friendly",
            " friendly",
            "Preserve leading space (streaming token)"
        ),
    ]
    
    print("Testing LLM Text Filter")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = filter.clean_text(input_text)
        
        if result == expected:
            print(f"✓ PASS: {description}")
            print(f"  Input:    '{input_text}'")
            print(f"  Output:   '{result}'")
            passed += 1
        else:
            print(f"✗ FAIL: {description}")
            print(f"  Input:    '{input_text}'")
            print(f"  Expected: '{expected}'")
            print(f"  Got:      '{result}'")
            failed += 1
        print()
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(test_text_filter())

