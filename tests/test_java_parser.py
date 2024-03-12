import re

public_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'
public_static_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*(?:public\s+static\s+)?(?:\w+\s+)?\w+\s+\w+\s*\((?:.*?)\)'
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

docstring = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public returnType functionName(dataType arg1, dataType arg2) {
"""

larger_docstring = """
/**
 * This is a multi-line comment.
 * Another line.
 * And another one.
 */
public static returnType functionName(dataType arg1, dataType arg2) {
"""


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

# Find the first match for either pattern in the Java code
# match = re.findall(public_static_fun, docstring_class, re.DOTALL)
