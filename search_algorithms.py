import time
from typing import List, Tuple, Dict, Set
import difflib
from models import Product
from collections import defaultdict
import bisect
import re
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

@dataclass
class SearchResult:
    products: List[Product]
    time_taken: float
    algorithm_name: str
    matches_found: int

class SearchAlgorithms:
    def __init__(self, products: List[Product]):
        self.products = products
        self._build_indices()
    
    def _build_indices(self):
        # Name index for exact matches
        self.name_index = defaultdict(set)
        # Brand index
        self.brand_index = defaultdict(set)
        # Category index
        self.category_index = defaultdict(set)
        # Price index (sorted list of (price, pid))
        self.price_index = []
        # Fuzzy search index
        self.fuzzy_index = []
        # Full text index for better matching
        self.full_text_index = defaultdict(set)
        
        for product in self.products:
            # Add to name index (split by words)
            words = product.name.lower().split()
            for word in words:
                self.name_index[word].add(product)
            
            # Add to brand index
            self.brand_index[product.brand.lower()].add(product)
            
            # Add to category index
            self.category_index[product.category.lower()].add(product)
            
            # Add to price index
            bisect.insort(self.price_index, (product.price, product.pid))
            
            # Add to fuzzy index
            self.fuzzy_index.append((product.name.lower(), product))
            
            # Add to full text index
            full_text = f"{product.name} {product.brand} {product.category} {product.description}".lower()
            for word in full_text.split():
                self.full_text_index[word].add(product)

    @lru_cache(maxsize=1000)
    def get_suggestions(self, query: str, max_suggestions: int = 5) -> List[str]:
        """Get search suggestions with caching for better performance"""
        if not query:
            return []
        
        query = query.lower().strip()
        suggestions = set()
        
        # Get exact matches first
        for name, _ in self.fuzzy_index:
            if query in name:
                suggestions.add(name)
        
        # Get brand matches
        for brand in self.brand_index.keys():
            if query in brand:
                suggestions.add(brand)
        
        # Get category matches
        for category in self.category_index.keys():
            if query in category:
                suggestions.add(category)
        
        # Use difflib for fuzzy matching if we don't have enough suggestions
        if len(suggestions) < max_suggestions:
            all_names = [name for name, _ in self.fuzzy_index]
            fuzzy_matches = difflib.get_close_matches(query, all_names, 
                                                    n=max_suggestions - len(suggestions), 
                                                    cutoff=0.6)
            suggestions.update(fuzzy_matches)
        
        # Sort suggestions by relevance
        def relevance_score(suggestion):
            # Exact match at start gets highest priority
            if suggestion.startswith(query):
                return (0, len(suggestion))
            # Contains query gets second priority
            if query in suggestion:
                return (1, len(suggestion))
            # Fuzzy match gets lowest priority
            return (2, len(suggestion))
        
        sorted_suggestions = sorted(suggestions, key=relevance_score)
        return sorted_suggestions[:max_suggestions]

    def linear_search(self, query: str) -> SearchResult:
        """Linear search through all products"""
        start_time = time.time()
        query = query.lower().strip()
        results = set()
        
        for product in self.products:
            # Check if query matches any part of the product
            if (query in product.name.lower() or
                query in product.brand.lower() or
                query in product.category.lower() or
                query in product.description.lower()):
                results.add(product)
        
        time_taken = time.time() - start_time
        return SearchResult(
            products=sorted(list(results), key=lambda x: x.name),
            time_taken=time_taken,
            algorithm_name="Linear Search",
            matches_found=len(results)
        )

    def indexed_search(self, query: str) -> SearchResult:
        """Search using pre-built indices"""
        start_time = time.time()
        query = query.lower().strip()
        results = set()
        
        # Split query into words
        words = query.split()
        
        # Search in name index
        for word in words:
            results.update(self.name_index[word])
        
        # Search in brand index
        results.update(self.brand_index[query])
        
        # Search in category index
        results.update(self.category_index[query])
        
        # Search in full text index
        for word in words:
            results.update(self.full_text_index[word])
        
        time_taken = time.time() - start_time
        return SearchResult(
            products=sorted(list(results), key=lambda x: x.name),
            time_taken=time_taken,
            algorithm_name="Indexed Search",
            matches_found=len(results)
        )

    def fuzzy_search(self, query: str) -> SearchResult:
        """Fuzzy search using difflib with improved precision"""
        start_time = time.time()
        query = query.lower().strip()
        results = set()
        
        # Split query into words for better matching
        query_words = query.split()
        
        for name, product in self.fuzzy_index:
            product_name = name.lower()
            product_words = product_name.split()
            
            # Calculate match scores
            exact_match_score = 0
            partial_match_score = 0
            fuzzy_match_score = 0
            
            # Check for exact matches first
            if query in product_name:
                exact_match_score = 1.0
            elif product_name in query:
                exact_match_score = 0.9
            
            # Check for partial matches
            matched_words = 0
            for q_word in query_words:
                if any(q_word in p_word for p_word in product_words):
                    matched_words += 1
            partial_match_score = matched_words / len(query_words)
            
            # Use SequenceMatcher for fuzzy matching only if no exact/partial matches
            if exact_match_score < 0.9 and partial_match_score < 0.5:
                fuzzy_match_score = difflib.SequenceMatcher(None, query, product_name).ratio()
            
            # Calculate final score
            final_score = max(exact_match_score, partial_match_score, fuzzy_match_score)
            
            # Add to results if score is high enough
            if final_score > 0.6:
                results.add(product)
        
        # Sort results by relevance
        sorted_results = sorted(
            list(results),
            key=lambda x: (
                not query.lower() in x.name.lower(),  # Exact matches first
                -len([w for w in query_words if w in x.name.lower()]),  # More matching words
                -difflib.SequenceMatcher(None, query, x.name.lower()).ratio()  # Better fuzzy match
            )
        )
        
        time_taken = time.time() - start_time
        return SearchResult(
            products=sorted_results,
            time_taken=time_taken,
            algorithm_name="Fuzzy Search",
            matches_found=len(results)
        )

    def regex_search(self, query: str) -> SearchResult:
        """Search using regular expressions"""
        start_time = time.time()
        try:
            # Create a case-insensitive pattern
            pattern = re.compile(query, re.IGNORECASE)
            results = set()
            
            for product in self.products:
                if (pattern.search(product.name) or
                    pattern.search(product.brand) or
                    pattern.search(product.category) or
                    pattern.search(product.description)):
                    results.add(product)
            
            time_taken = time.time() - start_time
            return SearchResult(
                products=sorted(list(results), key=lambda x: x.name),
                time_taken=time_taken,
                algorithm_name="Regex Search",
                matches_found=len(results)
            )
        except re.error:
            return SearchResult([], time.time() - start_time, "Regex Search", 0)

    def price_range_search(self, min_price: float, max_price: float) -> SearchResult:
        """Search products within a price range"""
        start_time = time.time()
        
        # Binary search for price range
        idx_start = bisect.bisect_left(self.price_index, (min_price, -float('inf')))
        idx_end = bisect.bisect_right(self.price_index, (max_price, float('inf')))
        
        results = []
        for price, pid in self.price_index[idx_start:idx_end]:
            product = next((p for p in self.products if p.pid == pid), None)
            if product:
                results.append(product)
        
        time_taken = time.time() - start_time
        return SearchResult(
            products=sorted(results, key=lambda x: x.price),
            time_taken=time_taken,
            algorithm_name="Price Range Search",
            matches_found=len(results)
        )

    def run_all_searches(self, query: str) -> Dict[str, SearchResult]:
        """Run all search algorithms and return their results"""
        # Normalize query
        query = query.strip()
        
        # Try to parse query as price range
        price_match = re.match(r'price:(\d+)-(\d+)', query.lower())
        if price_match:
            min_price, max_price = map(float, price_match.groups())
            return {"price_range": self.price_range_search(min_price, max_price)}
        
        # Run all text-based searches
        results = {
            "linear": self.linear_search(query),
            "indexed": self.indexed_search(query),
            "fuzzy": self.fuzzy_search(query),
            "regex": self.regex_search(query)
        }
        
        # Sort results by relevance across all algorithms
        for algo_name, result in results.items():
            if result.matches_found > 0:
                # Sort products by relevance
                result.products.sort(
                    key=lambda x: (
                        not query.lower() in x.name.lower(),  # Exact matches first
                        -len([w for w in query.split() if w in x.name.lower()]),  # More matching words
                        -difflib.SequenceMatcher(None, query, x.name.lower()).ratio()  # Better fuzzy match
                    )
                )
        
        # Remove empty results
        return {k: v for k, v in results.items() if v.matches_found > 0} 