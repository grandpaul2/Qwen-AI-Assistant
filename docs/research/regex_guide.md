# Regular Expressions (Regex) Guide

## Overview

Regular expressions are a powerful pattern-matching language used to search, match, and manipulate text. This guide provides a comprehensive reference for implementing regex in your application.

## Basic Syntax

### Literal Characters
- Most characters match themselves literally
- `hello` matches the exact string "hello"
- Case-sensitive by default (use flags for case-insensitive matching)

### Metacharacters
Characters with special meanings that need escaping (`\`) to match literally:

| Character | Meaning | Example |
|-----------|---------|---------|
| `.` | Matches any single character except newline | `a.c` matches "abc", "axc", "a5c" |
| `*` | Zero or more of preceding element | `ab*c` matches "ac", "abc", "abbc" |
| `+` | One or more of preceding element | `ab+c` matches "abc", "abbc" but not "ac" |
| `?` | Zero or one of preceding element | `ab?c` matches "ac", "abc" but not "abbc" |
| `^` | Start of string/line | `^hello` matches "hello" at start |
| `$` | End of string/line | `world$` matches "world" at end |
| `|` | Alternation (OR) | `cat|dog` matches "cat" or "dog" |

## Character Classes

### Basic Character Classes
- `[abc]` - Matches any single character: a, b, or c
- `[a-z]` - Matches any lowercase letter
- `[A-Z]` - Matches any uppercase letter
- `[0-9]` - Matches any digit
- `[a-zA-Z0-9]` - Matches any alphanumeric character

### Negated Character Classes
- `[^abc]` - Matches any character except a, b, or c
- `[^0-9]` - Matches any non-digit character

### Predefined Character Classes
| Class | Meaning | Equivalent |
|-------|---------|------------|
| `\d` | Any digit | `[0-9]` |
| `\D` | Any non-digit | `[^0-9]` |
| `\w` | Word character | `[a-zA-Z0-9_]` |
| `\W` | Non-word character | `[^a-zA-Z0-9_]` |
| `\s` | Whitespace character | `[ \t\n\r\f\v]` |
| `\S` | Non-whitespace character | `[^ \t\n\r\f\v]` |

## Quantifiers

### Basic Quantifiers
- `*` - Zero or more
- `+` - One or more  
- `?` - Zero or one (optional)

### Specific Quantifiers
- `{n}` - Exactly n times
- `{n,}` - n or more times
- `{n,m}` - Between n and m times (inclusive)

### Examples
```regex
\d{3}           # Exactly 3 digits
\d{2,4}         # 2 to 4 digits
[a-z]{1,}       # One or more lowercase letters
colou?r         # Matches "color" or "colour"
```

## Grouping and Capturing

### Groups
- `(pattern)` - Capturing group
- `(?:pattern)` - Non-capturing group
- `(pattern1|pattern2)` - Alternation within group

### Examples
```regex
(cat|dog)s?     # Matches "cat", "cats", "dog", "dogs"
(\d{3})-(\d{3})-(\d{4})  # Captures phone number parts
(?:Mr|Mrs|Dr)\.  # Non-capturing group for titles
```

## Anchors and Boundaries

| Anchor | Meaning |
|--------|---------|
| `^` | Start of string/line |
| `$` | End of string/line |
| `\b` | Word boundary |
| `\B` | Non-word boundary |
| `\A` | Start of string only |
| `\Z` | End of string only |

### Examples
```regex
^\d+$           # Entire string must be digits
\bword\b        # "word" as complete word only
\B@\B           # @ not at word boundaries
```

## Common Patterns

### Email Validation (Basic)
```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

### Phone Numbers
```regex
# US format: (123) 456-7890
^\(\d{3}\)\s\d{3}-\d{4}$

# International format: +1-234-567-8900
^\+\d{1,3}-\d{3}-\d{3}-\d{4}$
```

### URLs
```regex
^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$
```

### IP Address
```regex
^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
```

### Password Strength
```regex
# At least 8 chars, 1 upper, 1 lower, 1 digit, 1 special
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
```

### Credit Card Numbers
```regex
# Visa: 4xxx-xxxx-xxxx-xxxx
^4\d{3}-?\d{4}-?\d{4}-?\d{4}$

# MasterCard: 5xxx-xxxx-xxxx-xxxx
^5\d{3}-?\d{4}-?\d{4}-?\d{4}$
```

## Flags/Modifiers

Common regex flags across languages:

| Flag | Name | Description |
|------|------|-------------|
| `i` | Ignore case | Case-insensitive matching |
| `g` | Global | Find all matches, not just first |
| `m` | Multiline | ^ and $ match line breaks |
| `s` | Dotall | . matches newline characters |
| `x` | Extended | Ignore whitespace and comments |

## Lookarounds

### Positive Lookahead `(?=pattern)`
```regex
\d+(?=\s*dollars)   # Numbers followed by "dollars"
```

### Negative Lookahead `(?!pattern)`
```regex
\b\w+(?!ing\b)      # Words not ending with "ing"
```

### Positive Lookbehind `(?<=pattern)`
```regex
(?<=\$)\d+          # Numbers preceded by "$"
```

### Negative Lookbehind `(?<!pattern)`
```regex
(?<!un)\w+ly        # Words ending in "ly" not preceded by "un"
```

## Escaping Special Characters

To match literal special characters, escape with backslash:

```regex
\$\d+\.\d{2}        # Matches "$25.99"
\(555\) 123-4567    # Matches "(555) 123-4567"
```

Special characters that need escaping: `. ^ $ * + ? { } [ ] \ | ( )`

## Performance Considerations

### Best Practices
- Use specific character classes instead of `.` when possible
- Anchor patterns with `^` and `$` when matching entire strings
- Use non-capturing groups `(?:)` when you don't need to extract the match
- Be careful with nested quantifiers (catastrophic backtracking)

### Avoid
```regex
(.*)*               # Catastrophic backtracking
(.+)+               # Catastrophic backtracking
```

### Prefer
```regex
[^>]*               # Instead of .* when matching until >
\d+                 # Instead of .+ when expecting digits
```

## Language-Specific Implementation Notes

### JavaScript
```javascript
const regex = /pattern/flags;
const match = string.match(regex);
const replaced = string.replace(regex, 'replacement');
```

### Python
```python
import re
pattern = re.compile(r'pattern', re.FLAGS)
match = pattern.search(string)
replaced = pattern.sub('replacement', string)
```

### Java
```java
Pattern pattern = Pattern.compile("pattern", Pattern.FLAGS);
Matcher matcher = pattern.matcher(string);
boolean found = matcher.find();
```

## Testing and Debugging

### Recommended Tools
- **Online testers**: regex101.com, regexpal.com, regexr.com
- **IDE plugins**: Most modern IDEs have regex testing features
- **Command line**: `grep`, `sed`, `awk` for Unix/Linux systems

### Testing Strategy
1. Start with simple test cases
2. Test edge cases (empty strings, special characters)
3. Test performance with large datasets
4. Validate with real-world data samples

## Common Pitfalls

1. **Greedy vs Lazy Matching**
   - `.*` is greedy (matches as much as possible)
   - `.*?` is lazy (matches as little as possible)

2. **Escaping Issues**
   - Remember to escape special characters in patterns
   - Different languages may require different escaping

3. **Unicode Considerations**
   - `\w` may not include accented characters
   - Use Unicode categories for international text: `\p{L}` for letters

4. **Performance**
   - Complex patterns can be slow
   - Test with realistic data volumes

## Conclusion

Regular expressions are powerful but should be used judiciously. For complex parsing tasks, consider dedicated parsers. Always test thoroughly and document complex patterns for maintainability.

---

*This guide covers the most commonly used regex features. For advanced features and language-specific details, consult the documentation for your specific regex engine.*