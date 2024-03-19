import os
'''
Map classpath to corresponding .java file.
Results are saved, program not intented to run each time.
'''
def find_java_class_pairs():
    java_class_pairs = []
    # TODO: provide paths as arguments
    src_dir = '/Users/glacierali/repos/MEX/commons-lang/src/main/java/org/apache/commons/lang3'
    target_dir = '/Users/glacierali/repos/MEX/commons-lang/target/classes/org/apache/commons/lang3'
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.java'):
                java_file = os.path.join(root, file)
                class_file = java_file.replace(src_dir, target_dir).replace('.java', '.class')
                if os.path.exists(class_file):
                    java_class_pairs.append((java_file, class_file))
    return java_class_pairs

if __name__ == "__main__":
    java_class_pairs = find_java_class_pairs()
    with open('java_class_pairs.txt', 'w') as output_file:
        output_file.write('\n'.join('{} {}'.format(pair[0],pair[1]) for pair in java_class_pairs))
