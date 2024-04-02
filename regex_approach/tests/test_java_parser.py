import re

public_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*public\s+\w+\s+\w+\s*\((?:.*?)\)'
public_static_fun = r'/\*\*(?:(?!\*/).)*?\*/\s*(?:public\s+static\s+)?(?:\w+\s+)?\w+\s+\w+\s*\((?:.*?)\)'


# PUBLIC FUNCTIONS WITHOUT javadocS

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

# PRIVATE FUNCTIONS WITHOUT javadocS

priv_fun = """
private returnType functionName(dataType arg1, dataType arg2) {
"""

# PROTECTED FUNCTIONS WITHOUT javadocS
prot_fun_ = """
protected returnType functionName(dataType arg1, dataType arg2)
{
"""
prot_fun_return_val_arr = """
protected returnType[] functionName(dataType arg1, dataType arg2) 
{
"""


# javadocS PREPENDED FUNCTION
public_javadoc = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public returnValue functionName(dataType arg1, dataType arg2) {
"""

public_javadoc_awful_returnvalue = """
/**
 * This is a multi-line comment.
 * Another line.
 * Another lineee.
 */
public List<ActionResult<Map<String, long>>> functionName(dataType arg1, dataType arg2) {
"""

javadoc_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
public static returnType functionName(dataType arg1, dataType arg2) {
"""

# PRIVATE AND PROTECTED FUNCTIONS WITH javadoc

javadoc_private_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
private static returnType functionName(dataType arg1, dataType arg2) {
"""
javadoc_private_static_pattern = r'/\*\*(?:(?!\*/).)*?\*/\s*private\s+static\s+(\w+)\s+(\w+)\s*\((.*?)\)\s*\{'

javadoc_private = """
/**
 * This is a multi-line comment.
 * Another line.
 */
private returnType functionName(dataType arg1, dataType arg2) {
"""

# PRIVATE AND PROTECTED FUNCTIONS WITH javadoc
javadoc_protected_static = """
/**
 * This is a multi-line comment.
 * Another line.
 */
protected static returnType functionName(dataType arg1, dataType arg2) {
"""

javadoc_protected = """
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

javadoc_class = """

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.commons.lang3;

import java.util.Arrays;

/**
 * test and returns arrays in the fluent style.
 *
 * @since 3.14.0
 */
public final class ArrayFill {

    /**
     * Fills and returns the given array.
     *
     * @param a   the array to be filled.
     * @param val the value to be stored in all elements of the array.
     * @return the given array.
     * @see Arrays#fill(byte[],byte)
     */
    public static byte[] fill   (final byte[] a, final byte val) {
        Arrays.fill(a, val);
        return a;
    }
}
"""

public_class =  """
public class AnnotationUtils {
"""



match_all_pattern = r'(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'
javadoc_match_all_pattern = r'/\*\*.*?\*/\s*(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'

test = r'(?:/\*\*[^{;]*?\*/\s*)?.*public.*?\([\s\S]*?\)\s*{'
function_pattern = r'(?:/\*\*[^{;]*?\*/\s*)?.*(public|private).*?(?:(?!\*/)[^{;]).*?\([\s\S]*?\)\s*{'
# Combined, javadoc is optional
#match_all_pattern = r'(?:/\*\*.*?\*/\s*)?(public|private|static|protected|abstract|native|synchronized)\s+([a-zA-Z0-9<>._?, ]+)(?:\[\])*\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9<>\[\]._?, \n]*\)\s*([a-zA-Z0-9_ ,\n]*)\s*{'


array_utils = '''
/**
 * Operations on arrays, primitive arrays (like {@code int[]}) and
 * primitive wrapper arrays (like {@code Integer[]}).
 * <p>
 * This class tries to handle {@code null} input gracefully.
 * An exception will not be thrown for a {@code null}
 * array input. However, an Object array that contains a {@code null}
 * element may throw an exception. Each method documents its behavior.
 * </p>
 * <p>
 * #ThreadSafe#
 * </p>
 * @since 2.0
 */
public class ArrayUtils {

    /**
     * An empty immutable {@link Type} array.
     *
     * @since 3.10
     */
    public static final Type[] EMPTY_TYPE_ARRAY = {};

    /**
     * The index value when an element is not found in a list or array: {@code -1}.
     * This value is returned by methods in this class and can also be used in comparisons with values returned by
     * various method from {@link java.util.List}.
     */
    public static final int INDEX_NOT_FOUND = -1;

    /**
     * Copies the given array and adds the given element at the end of the new array.
     * <p>
     * The new array contains the same elements of the input
     * array plus the given element in the last position. The component type of
     * the new array is the same as that of the input array.
     * </p>
     * <p>
     * If the input array is {@code null}, a new one element array is returned
     * whose component type is the same as the element.
     * </p>
     * <pre>
     * ArrayUtils.add(null, true)          = [true]
     * ArrayUtils.add([true], false)       = [true, false]
     * ArrayUtils.add([true, false], true) = [true, false, true]
     * </pre>
     *
     * @param array  the array to copy and add the element to, may be {@code null}
     * @param element  the object to add at the last index of the new array
     * @return A new array containing the existing elements plus the new element
     * @since 2.1
     */
    public static boolean[] add(final boolean[] array, final boolean element) {
        final boolean[] newArray = (boolean[]) copyArrayGrow1(array, Boolean.TYPE);
        newArray[newArray.length - 1] = element;
        return newArray;
    }

}
'''
print("PUBLIC CLASS VAR")
#match = re.search(function_pattern, public_class_var)
#all = re.findall(function_pattern, public_class_var)
print("all: ", all[0])

