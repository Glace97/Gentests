import re

public_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'
public_static_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*(?:public\s+static\s+)?(?:\w+\s+)?\w+\s+\w+\s*\((?:.*?)\)'


# PUBLIC FUNCTIONS WITHOUT DOCSTRINGS

fun_return_val = """
public returnType functionName(dataType arg1, dataType arg2)
"""

fun_opening_bracket = """
public returnType functionName(dataType arg1, dataType arg2) {
"""

fun_opening_bracket_newline = """
public returnType functionName(dataType arg1, dataType arg2) 
{
"""

fun_static_return_val = """
public static returnType functionName(dataType arg1, dataType arg2) 
{
"""


# DOCSTRINGS PREPENDED FUNCTION
docstring = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public returnType functionName(dataType arg1, dataType arg2) {
"""

docstring_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public static returnType functionName(dataType arg1, dataType arg2) {
"""

docstring_class = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public class AnnotationUtils {
"""


# PRIVATE AND PROTECTED FUNCTIONS WITH DOCSTRING

docstring_private_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
private static returnType functionName(dataType arg1, dataType arg2) {
"""
docstring_private_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

docstring_private = """
/**
 * This is a multi-line comment.
 * Another line.
 */
private returnType functionName(dataType arg1, dataType arg2) {
"""
docstring_private_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

# PRIVATE AND PROTECTED FUNCTIONS WITH DOCSTRING

docstring_protected_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
protected static returnType functionName(dataType arg1, dataType arg2) {
"""
docstring_protected_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*protected\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

docstring_protected = """
/**
 * This is a multi-line comment.
 * Another line.
 */
protected returnType functionName(dataType arg1, dataType arg2) {
"""
docstring_protected_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*protected\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

# Find the first match for either pattern in the Java code
match = re.findall(docstring_protected_pattern, docstring_protected, re.DOTALL)
print(match)