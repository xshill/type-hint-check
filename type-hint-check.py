#!/usr/bin/env python3
import argparse
import ast
import glob
import json
import pathlib
import sys
import typing


class TypeHintVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issue_stack = []
        self.return_stack = []
        self.function_issues: typing.Dict[typing.Union[ast.FunctionDef, ast.AsyncFunctionDef], [str]] = {}


    def visit(self, node: ast.AST):
        is_function = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    
        if is_function:
            self.issue_stack.append([])
            self.return_stack.append([])
        elif isinstance(node, ast.arg):
            if node.annotation is None and node.arg != "self":
                self.issue_stack[-1].append(f"Missing type hint for '{node.arg}'")
        elif isinstance(node, ast.Return):
            self.return_stack[-1].append(node.value)

        super().visit(node)

        if is_function:
            issues = self.issue_stack[-1]

            if any(return_value is not None for return_value in self.return_stack[-1]) and node.returns is None:
                issues.insert(0, f"Missing type hint for return value")

            if len(issues) > 0:
                self.function_issues[node] = issues

            self.issue_stack.pop()
            self.return_stack.pop()
    

    def create_json_report(self) -> dict:
        issue_list: [dict] = []

        for function, issues in self.function_issues.items():
            issue_dict = {
                "type": "function",
                "name": function.name,
                "line": function.lineno,
                "column": function.col_offset,
                "issues": issues.copy(),
            }

            issue_list.append(issue_dict)
        
        return issue_list


def handle_file(path: pathlib.Path) -> dict:
    with open(path, "r") as f:
        code = f.read()
    
    tree = ast.parse(code, filename=path)
    visitor = TypeHintVisitor()
    visitor.generic_visit(tree)
    return visitor.create_json_report()


def handle_file_list(paths: [pathlib.Path]) -> [dict]:
    issues = []

    for path in paths:
        file_report = handle_file(path)

        if file_report:
            issues.append({
                "file": str(path.resolve()),
                "report": file_report,
            })
    
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Files or directories to check", nargs="+")
    parser.add_argument("-r", "--recursive", help="Check directories recursively", action="store_true")

    args = parser.parse_args()

    paths = [pathlib.Path(path) for path in args.path]

    for index in range(len(paths)):
        path = paths[index]

        if path.is_dir():
            if not args.recursive:
                print(f"{path} is a directory. Use -r if you want to check directories recursively.", file=sys.stderr)
                sys.exit(1)
            else:
                files = path.glob("**/*.py")
                paths[index : index + 1] = files

    issues = handle_file_list(paths)
    
    print(json.dumps(issues, indent = 4))


if __name__ == "__main__":
    main()