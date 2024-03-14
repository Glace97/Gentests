import re

public_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'
public_static_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*(?:public\s+static\s+)?(?:\w+\s+)?\w+\s+\w+\s*\((?:.*?)\)'


# PUBLIC FUNCTIONS WITHOUT DOCSTRINGS

public_fun = """
public int functionName(dataType arg1, dataType arg2) {
"""

public_static= """
public static returnType functionName(dataType arg1, dataType arg2) 
{
"""

awful_returnval = """
    public List<ActionResult<Map<String, long>>> functionName(dataType arg1, dataType arg2) 
    { 
"""
public_fun_array_returnval = """
public returnType[] functionName(dataType arg1, dataType arg2) {
"""

# PRIVATE FUNCTIONS WITHOUT DOCSTRINGS

priv_fun = """
private returnType functionName(dataType arg1, dataType arg2) {
"""

# PROTECTED FUNCTIONS WITHOUT DOCSTRINGS
prot_fun_ = """
protected returnType functionName(dataType arg1, dataType arg2)
{
"""
prot_fun_return_val_arr = """
protected returnType[] functionName(dataType arg1, dataType arg2) 
{
"""


# DOCSTRINGS PREPENDED FUNCTION
public_docstring = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public returnValue functionName(dataType arg1, dataType arg2) {
"""

public_docstring_awful_returnvalue = """
/**
 * This is a multi-line comment.
 * Another line.
 * Another lineee.
 */
public List<ActionResult<Map<String, long>>> functionName(dataType arg1, dataType arg2) {
"""

docstring_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public static returnType functionName(dataType arg1, dataType arg2) {
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

# PRIVATE AND PROTECTED FUNCTIONS WITH DOCSTRING
docstring_protected_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
protected static returnType functionName(dataType arg1, dataType arg2) {
"""

docstring_protected = """
/**
 * This is a multi-line comment.
 * Another line.
 *fnfea
 */
protected returnType functionName(dataType arg1, dataType arg2, final dataType arg3) {
"""

# SHOULD NEVER MATCH

constructor = """
public className(dataType arg1, dataType arg2, final dataType arg3) {
"""

docstring_class = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public class AnnotationUtils {
"""

public_class =  """
public class AnnotationUtils {
"""

# Does not match against methods with arrays as returnvalue?
#match_all_pattern = r'(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'
#docstring_match_all_pattern = r'/\*\*.*?\*/\s*(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'


# Combined, docstring is optional
match_all_pattern = r'(?:/\*\*.*?\*/\s*)?(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'



# Find the first match for either pattern in the Java code
#match = re.findall(docstring_match_all_pattern, docstring_class, re.DOTALL)
#match = re.findall(match_all_pattern, )
match = re.findall(match_all_pattern, docstring_class)

print(match)