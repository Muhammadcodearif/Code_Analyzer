from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import ast
import re
import os
import json

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_js_file(content):
    """Analyze JavaScript/React code for clean code practices."""
    score = {
        "naming": 0,
        "modularity": 0,
        "comments": 0,
        "formatting": 0,
        "reusability": 0,
        "best_practices": 0
    }
    recommendations = []
    
  
    camel_case_pattern = re.compile(r'(const|let|var)\s+([a-z][a-zA-Z0-9]*)\s*=')
    pascal_case_pattern = re.compile(r'function\s+([A-Z][a-zA-Z0-9]*)')
    component_pattern = re.compile(r'const\s+([A-Z][a-zA-Z0-9]*)\s*=\s*(React\.createClass|\(\)|function)')
    
    variable_names = camel_case_pattern.findall(content)
    component_names = component_pattern.findall(content) + pascal_case_pattern.findall(content)
    

    bad_var_names = [var[1] for var in variable_names if not re.match(r'^[a-z][a-zA-Z0-9]*$', var[1])]
    if bad_var_names:
        recommendations.append(f"Use consistent camelCase for variables: {', '.join(bad_var_names[:3])}")
        score["naming"] = max(0, 10 - min(5, len(bad_var_names)))
    else:
        score["naming"] = 10
    
   
    bad_component_names = [comp[0] if isinstance(comp, tuple) else comp for comp in component_names 
                          if not re.match(r'^[A-Z][a-zA-Z0-9]*$', comp[0] if isinstance(comp, tuple) else comp)]
    if bad_component_names and score["naming"] > 2:
        recommendations.append(f"Use PascalCase for component names: {', '.join(bad_component_names[:3])}")
        score["naming"] = max(0, score["naming"] - min(3, len(bad_component_names)))
    
    function_pattern = re.compile(r'(function\s+\w+\s*\([^)]*\)\s*{|\(\s*[^)]*\)\s*=>\s*{)([^}]*)}', re.DOTALL)
    functions = function_pattern.findall(content)
    
    long_functions = [fn[:20] + "..." for fn, body in functions if body.count('\n') > 20]
    if long_functions:
        recommendations.append(f"Break down large functions into smaller ones: {', '.join(long_functions[:2])}")
        score["modularity"] = max(0, 20 - min(10, len(long_functions) * 5))
    else:
        score["modularity"] = 20
    

    comment_lines = len(re.findall(r'(//.*$|/\*[\s\S]*?\*/)', content, re.MULTILINE))
    code_lines = content.count('\n') + 1
    
    comment_ratio = comment_lines / max(1, code_lines)
    if comment_ratio < 0.1:
        recommendations.append("Add more comments to explain complex logic and component purposes")
        score["comments"] = int(comment_ratio * 200) 
    else:
        score["comments"] = min(20, int(comment_ratio * 200))
    
   
    inconsistent_indent = len(re.findall(r'^ {1,3}\S', content, re.MULTILINE))
    if inconsistent_indent > 0:
        recommendations.append("Use consistent indentation (2 or 4 spaces)")
        score["formatting"] = max(0, 15 - min(15, inconsistent_indent * 3))
    else:
        score["formatting"] = 15
    
    repeated_code_blocks = []
    lines = content.split('\n')
    line_hash = {}
    
    for i in range(len(lines)):
        if len(lines[i].strip()) > 10:
            line = lines[i].strip()
            if line in line_hash:
                line_hash[line].append(i)
            else:
                line_hash[line] = [i]
    
    for line, occurrences in line_hash.items():
        if len(occurrences) > 3:
            repeated_code_blocks.append(line[:20] + "...")
    
    if repeated_code_blocks:
        recommendations.append(f"Extract repeated code into reusable functions: {', '.join(repeated_code_blocks[:2])}")
        score["reusability"] = max(0, 15 - min(10, len(repeated_code_blocks) * 2))
    else:
        score["reusability"] = 15
    
  
    has_prop_types = "PropTypes" in content
    uses_inline_styles = len(re.findall(r'style={{', content)) > 3
    has_too_many_state_updates = len(re.findall(r'setState\(', content)) > 10
    
    if not has_prop_types:
        recommendations.append("Add PropTypes to validate component props")
        score["best_practices"] = max(0, score["best_practices"] - 5)
    else:
        score["best_practices"] = 5
    
    if uses_inline_styles:
        recommendations.append("Avoid inline styles, use CSS classes instead")
        score["best_practices"] = max(0, score["best_practices"] - 5)
    else:
        score["best_practices"] += 5
    
    if has_too_many_state_updates:
        recommendations.append("Minimize state updates, consider using useReducer for complex state")
        score["best_practices"] = max(0, score["best_practices"] - 5)
    else:
        score["best_practices"] += 5
    
    # Add more best practices
    if "componentWillMount" in content or "componentWillUpdate" in content:
        recommendations.append("Replace deprecated lifecycle methods with newer alternatives")
        score["best_practices"] = max(0, score["best_practices"] - 5)
    else:
        score["best_practices"] += 5
    
    return score, recommendations

def analyze_py_file(content):
    """Analyze Python/FastAPI code for clean code practices."""
    score = {
        "naming": 0,
        "modularity": 0,
        "comments": 0,
        "formatting": 0,
        "reusability": 0,
        "best_practices": 0
    }
    recommendations = []
    
    try:
  
        tree = ast.parse(content)
        
     
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        variables = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)]
        
    
        bad_func_names = [func.name for func in functions if not re.match(r'^[a-z][a-z0-9_]*$', func.name)]
        bad_class_names = [cls.name for cls in classes if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls.name)]
        
        if bad_func_names:
            recommendations.append(f"Use snake_case for function names: {', '.join(bad_func_names[:3])}")
            score["naming"] = max(0, 10 - min(5, len(bad_func_names)))
        else:
            score["naming"] = 5
        
        if bad_class_names:
            recommendations.append(f"Use PascalCase for class names: {', '.join(bad_class_names[:3])}")
            score["naming"] = max(0, score["naming"] - min(5, len(bad_class_names)))
        else:
            score["naming"] += 5
        
       
        long_functions = [func.name for func in functions if len(func.body) > 15]
        if long_functions:
            recommendations.append(f"Function{'s' if len(long_functions) > 1 else ''} too long, consider refactoring: {', '.join(long_functions[:3])}")
            score["modularity"] = max(0, 20 - min(10, len(long_functions) * 3))
        else:
            score["modularity"] = 20
        
  
        docstring_count = sum(1 for func in functions if ast.get_docstring(func))
        
        if functions and docstring_count / len(functions) < 0.5:
            recommendations.append("Add docstrings to functions for better documentation")
            score["comments"] = int((docstring_count / max(1, len(functions))) * 20)
        else:
            score["comments"] = 20
        
       
        lines = content.split('\n')
        inconsistent_indent = 0
        
        for i in range(1, len(lines)):
            if lines[i].startswith(' ') and not (lines[i].startswith('    ') or lines[i].startswith('  ')):
                inconsistent_indent += 1
        
        if inconsistent_indent > 0:
            recommendations.append("Use consistent indentation (PEP 8 recommends 4 spaces)")
            score["formatting"] = max(0, 15 - min(15, inconsistent_indent * 3))
        else:
            score["formatting"] = 15
        

        function_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        defined_functions = set(func.name for func in functions)
        used_functions = set()
        
        for call in function_calls:
            if isinstance(call.func, ast.Name) and call.func.id in defined_functions:
                used_functions.add(call.func.id)
        
        unused_functions = defined_functions - used_functions
        
        if unused_functions and len(defined_functions) > 2:
            recommendations.append(f"Remove or utilize unused functions: {', '.join(list(unused_functions)[:3])}")
            score["reusability"] = max(0, 15 - min(10, len(unused_functions) * 3))
        else:
            score["reusability"] = 15
        
   
        is_fastapi = "FastAPI" in content or "fastapi" in content
        
        if is_fastapi:
           
            has_error_handling = "HTTPException" in content or "ValidationError" in content
            if not has_error_handling:
                recommendations.append("Add proper error handling with HTTPException")
                score["best_practices"] = 5
            else:
                score["best_practices"] = 10
            
           
            has_dependency = "Depends" in content
            if not has_dependency and len(functions) > 3:
                recommendations.append("Use dependency injection for better code organization")
                score["best_practices"] = max(0, score["best_practices"] + 5)
            else:
                score["best_practices"] += 5
            
           
            has_response_model = "response_model" in content
            if not has_response_model:
                recommendations.append("Define response models with Pydantic for better API documentation")
                score["best_practices"] = max(0, score["best_practices"] + 2)
            else:
                score["best_practices"] += 5
        else:
    
            global_vars = len([node for node in ast.walk(tree) if isinstance(node, ast.Global)])
            if global_vars > 0:
                recommendations.append("Avoid using global variables")
                score["best_practices"] = max(0, 10 - min(5, global_vars * 2))
            else:
                score["best_practices"] = 10
            
           
            imports = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            if imports > 15:
                recommendations.append("Too many imports, consider refactoring or organizing the code")
                score["best_practices"] = max(0, score["best_practices"] + 5)
            else:
                score["best_practices"] += 5
            
       
            try_blocks = len([node for node in ast.walk(tree) if isinstance(node, ast.Try)])
            if try_blocks == 0 and len(functions) > 3:
                recommendations.append("Add exception handling for more robust code")
                score["best_practices"] = max(0, score["best_practices"] + 2)
            else:
                score["best_practices"] += 5
        
    except SyntaxError:
        recommendations.append("Fix syntax errors in the code before analysis")
        for key in score:
            score[key] = 0
    
    return score, recommendations[:5] 

@app.post("/analyze-code")
async def analyze_code(file: UploadFile = File(...)):
    """
    Analyze uploaded code file for clean code practices.
    Returns a score out of 100 and recommendations for improvement.
    """
    # Check file extension
    filename = file.filename
    if not filename.endswith(('.js', '.jsx', '.py')):
        raise HTTPException(
            status_code=400, 
            detail="Only .js, .jsx or .py files are supported"
        )
    
    # Read file content
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # Analyze based on file type
    if filename.endswith(('.js', '.jsx')):
        breakdown, recommendations = analyze_js_file(content_str)
    else:
        breakdown, recommendations = analyze_py_file(content_str)
    
    
    overall_score = sum(breakdown.values())
    
    
    result = {
        "overall_score": overall_score,
        "breakdown": breakdown,
        "recommendations": recommendations[:5]  
    }
    
    return result

@app.get("/")
async def root():
    return {"message": "Clean Code Analyzer API - Upload a file to /analyze-code"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)