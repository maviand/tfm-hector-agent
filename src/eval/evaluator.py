import json
import difflib
from typing import Dict, Any

def fuzzy_match_score(str1: str, str2: str) -> float:
    """Returns a similarity score between 0.0 and 1.0 using difflib."""
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def evaluate_extraction(extracted: Dict[str, Any], golden: Dict[str, Any]) -> Dict[str, float]:
    """
    Compares an extracted JSON dictionary against a golden truth dictionary.
    Returns a dictionary of scores for key fields.
    """
    scores = {}
    
    # Exact matches for categorical/boolean data
    scores['category'] = 1.0 if extracted.get('category') == golden.get('category') else 0.0
    scores['judicial_claim_present'] = 1.0 if extracted.get('judicial_claim_present') == golden.get('judicial_claim_present') else 0.0
    scores['subrogation_opportunity'] = 1.0 if extracted.get('subrogation_opportunity') == golden.get('subrogation_opportunity') else 0.0
    
    # Numeric matching
    ext_amt = extracted.get('normalized_amount_usd')
    gold_amt = golden.get('normalized_amount_usd')
    if ext_amt is not None and gold_amt is not None:
        # Give full points if within 1% difference
        diff = abs(ext_amt - gold_amt)
        scores['normalized_amount_usd'] = 1.0 if diff < (0.01 * gold_amt) else 0.0
    else:
        scores['normalized_amount_usd'] = 1.0 if ext_amt == gold_amt else 0.0
        
    # Fuzzy match for descriptive fields
    scores['description'] = fuzzy_match_score(
        extracted.get('description', ''),
        golden.get('description', '')
    )
    
    # Calculate overall average
    if scores:
        scores['overall_accuracy'] = sum(scores.values()) / len(scores)
    else:
        scores['overall_accuracy'] = 0.0
        
    return scores
