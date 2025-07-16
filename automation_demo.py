#!/usr/bin/env python3
"""
DevO Chat Automation Examples
Demonstrates various automation tasks using local LLM
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from local_llm import LocalLLMManager, AutomationManager
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    LOCAL_LLM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install torch transformers rich")
    LOCAL_LLM_AVAILABLE = False
    sys.exit(1)

console = Console()

def demonstrate_code_generation():
    """Demonstrate automated code generation"""
    console.print("\n[bold cyan]🚀 Code Generation Demo[/bold cyan]")
    
    tasks = [
        "Create a REST API endpoint for user authentication",
        "Write a function to validate email addresses",
        "Generate a class for handling database connections",
        "Create a decorator for logging function calls",
        "Write unit tests for a calculator function"
    ]
    
    # Let user choose or input custom task
    console.print("\n[yellow]Choose a task or enter your own:[/yellow]")
    for i, task in enumerate(tasks, 1):
        console.print(f"{i}. {task}")
    console.print("6. Custom task")
    
    choice = Prompt.ask("Select option", choices=[str(i) for i in range(1, 7)], default="1")
    
    if choice == "6":
        task = Prompt.ask("Enter your custom task")
    else:
        task = tasks[int(choice) - 1]
    
    language = Prompt.ask("Programming language", default="python")
    
    return task, language

def demonstrate_code_fixing():
    """Demonstrate automated code fixing"""
    console.print("\n[bold cyan]🔧 Code Fixing Demo[/bold cyan]")
    
    # Example buggy code
    buggy_examples = {
        "1": {
            "code": """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# This will cause division by zero error
result = calculate_average([])
print(result)
""",
            "error": "ZeroDivisionError: division by zero"
        },
        "2": {
            "code": """
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

# This doesn't handle potential errors
data = fetch_data("https://invalid-url.com")
print(data)
""",
            "error": "ConnectionError: Failed to establish a new connection"
        },
        "3": {
            "code": """
def process_file(filename):
    file = open(filename, 'r')
    content = file.read()
    return content.upper()

# This doesn't close the file properly
result = process_file("test.txt")
print(result)
""",
            "error": "Resource leak: file not properly closed"
        }
    }
    
    console.print("\n[yellow]Choose buggy code to fix:[/yellow]")
    for key, example in buggy_examples.items():
        console.print(f"{key}. {example['error']}")
    console.print("4. Enter custom code")
    
    choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
    
    if choice == "4":
        console.print("[yellow]Enter your code (press Enter twice to finish):[/yellow]")
        code_lines = []
        empty_line_count = 0
        
        while empty_line_count < 2:
            line = input()
            if line == "":
                empty_line_count += 1
            else:
                empty_line_count = 0
            code_lines.append(line)
        
        code = "\n".join(code_lines[:-2])
        error = Prompt.ask("Describe the error")
    else:
        example = buggy_examples[choice]
        code = example["code"]
        error = example["error"]
    
    return code, error

def demonstrate_code_optimization():
    """Demonstrate code optimization"""
    console.print("\n[bold cyan]⚡ Code Optimization Demo[/bold cyan]")
    
    # Example code that can be optimized
    optimization_examples = {
        "1": """
def find_duplicates(list1, list2):
    duplicates = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                duplicates.append(item1)
    return duplicates
""",
        "2": """
def calculate_sum(numbers):
    result = 0
    for i in range(len(numbers)):
        result = result + numbers[i]
    return result
""",
        "3": """
import time

def slow_fibonacci(n):
    if n <= 1:
        return n
    return slow_fibonacci(n-1) + slow_fibonacci(n-2)

# This is very slow for large numbers
result = slow_fibonacci(30)
print(result)
"""
    }
    
    console.print("\n[yellow]Choose code to optimize:[/yellow]")
    console.print("1. Nested loop optimization")
    console.print("2. List iteration optimization")
    console.print("3. Fibonacci performance optimization")
    console.print("4. Enter custom code")
    
    choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
    
    if choice == "4":
        console.print("[yellow]Enter your code (press Enter twice to finish):[/yellow]")
        code_lines = []
        empty_line_count = 0
        
        while empty_line_count < 2:
            line = input()
            if line == "":
                empty_line_count += 1
            else:
                empty_line_count = 0
            code_lines.append(line)
        
        code = "\n".join(code_lines[:-2])
    else:
        code = optimization_examples[choice]
    
    focus = Prompt.ask("Optimization focus", 
                      choices=["performance", "readability", "memory", "maintainability"], 
                      default="performance")
    
    return code, focus

def main():
    """Main demonstration function"""
    if not LOCAL_LLM_AVAILABLE:
        console.print("[red]❌ Local LLM not available. Please run setup first.[/red]")
        return
    
    console.print(Panel.fit(
        "[bold green]DevO Chat Automation Demo[/bold green]\n"
        "This demo shows the automation capabilities of Enhanced DevO Chat.\n\n"
        "[cyan]Features demonstrated:[/cyan]\n"
        "• 🚀 Automated code generation\n"
        "• 🔧 Intelligent code fixing\n"
        "• ⚡ Code optimization\n"
        "• 🤖 Local AI processing\n\n"
        "[yellow]Note: First run may take a while as models are loaded.[/yellow]",
        title="🤖 Automation Demo",
        border_style="green"
    ))
    
    if not Confirm.ask("Continue with automation demo?"):
        console.print("[yellow]Demo cancelled.[/yellow]")
        return
    
    # Initialize Local LLM
    console.print("\n[cyan]🤖 Initializing Local LLM...[/cyan]")
    try:
        llm = LocalLLMManager()
        
        # Try to setup CodeLlama via Ollama first, then fallback to Transformers
        if not llm.setup_model("codellama", "ollama"):
            console.print("[yellow]Ollama setup failed, trying Transformers...[/yellow]")
            if not llm.setup_model("codellama", "transformers"):
                console.print("[red]❌ Could not initialize any local LLM[/red]")
                return
        
        automation = AutomationManager(llm)
        console.print("[green]✅ Local LLM initialized successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error initializing LLM: {e}[/red]")
        return
    
    while True:
        console.print("\n[bold cyan]🤖 DevO Automation Menu[/bold cyan]")
        console.print("1. 🚀 Code Generation")
        console.print("2. 🔧 Code Fixing") 
        console.print("3. ⚡ Code Optimization")
        console.print("4. 🔄 Switch Model")
        console.print("5. ℹ️  Model Status")
        console.print("6. 🚪 Exit")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"], default="1")
        
        try:
            if choice == "1":
                task, language = demonstrate_code_generation()
                console.print(f"\n[cyan]🚀 Generating {language} code for: {task}[/cyan]")
                
                result = automation.generate_code(task, language)
                console.print(Panel(
                    Syntax(result, language, theme="monokai", line_numbers=True),
                    title=f"Generated {language.title()} Code",
                    border_style="green"
                ))
                
            elif choice == "2":
                code, error = demonstrate_code_fixing()
                console.print(f"\n[cyan]🔧 Fixing code with error: {error}[/cyan]")
                
                result = automation.fix_code_issues(code, error)
                console.print(Panel(
                    result,
                    title="Fixed Code with Explanation",
                    border_style="green"
                ))
                
            elif choice == "3":
                code, focus = demonstrate_code_optimization()
                console.print(f"\n[cyan]⚡ Optimizing code for: {focus}[/cyan]")
                
                result = automation.optimize_code(code, focus)
                console.print(Panel(
                    result,
                    title=f"Optimized Code ({focus})",
                    border_style="green"
                ))
                
            elif choice == "4":
                console.print("\n[cyan]🔄 Available models:[/cyan]")
                available = llm.list_available_models()
                console.print(available)
                
                model_name = Prompt.ask("Enter model name", default="codellama")
                provider = Prompt.ask("Enter provider", choices=["ollama", "transformers"], default="ollama")
                
                if llm.setup_model(model_name, provider):
                    console.print(f"[green]✅ Switched to {model_name} via {provider}[/green]")
                else:
                    console.print("[red]❌ Failed to switch model[/red]")
                
            elif choice == "5":
                status = llm.get_status()
                console.print(Panel(
                    f"Current Provider: {status.get('current_provider', 'None')}\n"
                    f"Current Model: {status.get('current_model', 'None')}\n"
                    f"Ollama Running: {status.get('ollama_running', False)}",
                    title="Model Status",
                    border_style="blue"
                ))
                
            elif choice == "6":
                console.print("[green]👋 Thanks for trying DevO Automation![/green]")
                break
                
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            console.print("[yellow]Please try again or check your setup.[/yellow]")

if __name__ == "__main__":
    main()
