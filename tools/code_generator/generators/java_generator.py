"""
Simplified Java Project Generator

Only creates minimal project structure, lets LLM generate actual implementation files.
No dummy test files are created automatically.
"""

import os
from typing import Dict, List
from .base_generator import BaseProjectGenerator


class JavaProjectGenerator(BaseProjectGenerator):
    """Simplified generator for Java projects - no automatic test file generation"""
    
    def __init__(self):
        super().__init__()
        self.language = 'java'
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str) -> Dict[str, str]:
        """Generate minimal Java project structure - only essential files, no dummy tests"""
        created_files = {}
        
        # Create essential project files for Java
        # 1. Create pom.xml for Maven project
        pom_content = self._create_pom_xml_content(product_name)
        pom_file = os.path.join(project_dir, "pom.xml")
        with open(pom_file, 'w', encoding='utf-8') as f:
            f.write(pom_content)
        created_files["pom"] = pom_file
        
        # 2. Create src directory structure
        src_main_java = os.path.join(project_dir, "src", "main", "java")
        os.makedirs(src_main_java, exist_ok=True)
        
        # 3. Create .gitignore for Java projects
        gitignore_content = """target/
*.class
*.jar
*.war
.classpath
.project
.settings/
*.iml
.idea/"""
        gitignore_file = os.path.join(project_dir, ".gitignore")
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        created_files["gitignore"] = gitignore_file
        
        # 4. Create README with project instructions
        readme_file = os.path.join(project_dir, "README.md")
        readme_content = self._create_project_readme(product_name, scenarios)
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_pom_xml_content(self, product_name: str) -> str:
        """Create pom.xml for Maven project with common dependencies"""
        artifact_id = product_name.lower().replace(' ', '-')
        java_version = self.get_language_version('java')
        packages = self.get_packages_for_language(self.language)
        
        # Create properties section
        properties_xml = []
        properties_xml.append(f"        <maven.compiler.source>{java_version}</maven.compiler.source>")
        properties_xml.append(f"        <maven.compiler.target>{java_version}</maven.compiler.target>")
        properties_xml.append("        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>")
        
        for prop_name, prop_version in packages.items():
            if prop_name.endswith('.version'):
                properties_xml.append(f"        <{prop_name}>{prop_version}</{prop_name}>")
        
        # Create dependencies section
        dependencies_xml = []
        
        # Core utilities
        dependencies_xml.append(f'''        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>${{commons-lang3.version}}</version>
        </dependency>''')
        
        # JSON processing
        dependencies_xml.append(f'''        
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>${{jackson.version}}</version>
        </dependency>''')
        
        # HTTP client
        dependencies_xml.append(f'''        
        <dependency>
            <groupId>org.apache.httpcomponents.client5</groupId>
            <artifactId>httpclient5</artifactId>
            <version>${{httpclient5.version}}</version>
        </dependency>''')
        
        # Logging
        dependencies_xml.append(f'''        
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${{slf4j.version}}</version>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <version>${{logback.version}}</version>
        </dependency>''')
        
        # Configuration
        dependencies_xml.append(f'''        
        <dependency>
            <groupId>org.yaml</groupId>
            <artifactId>snakeyaml</artifactId>
            <version>${{snakeyaml.version}}</version>
        </dependency>''')
        
        # Testing dependencies - use only configured test packages
        test_packages = self.package_versions.get_test_packages_for_language(self.language)
        for package_key, version in test_packages.items():
            if package_key == 'junit.version':
                dependencies_xml.append(f'''        
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>${{{package_key}}}</version>
            <scope>test</scope>
        </dependency>''')
            elif package_key == 'mockito.version':
                dependencies_xml.append(f'''        
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>${{{package_key}}}</version>
            <scope>test</scope>
        </dependency>''')
            elif package_key == 'assertj.version':
                dependencies_xml.append(f'''        
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <version>${{{package_key}}}</version>
            <scope>test</scope>
        </dependency>''')
        
        properties_section = '\n'.join(properties_xml)
        dependencies_section = '\n'.join(dependencies_xml)
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>{artifact_id}</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <name>{product_name}</name>
    <description>{product_name} - Java Application</description>
    
    <properties>
{properties_section}
    </properties>
    
    <dependencies>
{dependencies_section}
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-exec-plugin</artifactId>
                <version>3.1.0</version>
                <configuration>
                    <mainClass>com.example.Main</mainClass>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>'''
    
    def _create_project_readme(self, product_name: str, scenarios: List[str]) -> str:
        """Create project README"""
        artifact_id = product_name.lower().replace(' ', '-')
        scenarios_list = '\n'.join(f'{i+1}. **{scenario}**' for i, scenario in enumerate(scenarios))
        
        return f'''# {product_name} - Java Application

This is a Java application for **{product_name}**.

## 📋 Functional Requirements

{scenarios_list}

## 🚀 Building and Running

### Prerequisites
- Java 17 or higher
- Maven 3.8 or higher

### Building
```bash
# Compile the project
mvn compile

# Package into JAR
mvn package
```

### Running
```bash
# Run the application
mvn exec:java

# Or run the JAR file
java -jar target/{artifact_id}-1.0.0.jar
```

### Development
```bash
# Clean build
mvn clean compile

# Run tests (when test files are created)
mvn test
```

## 📖 Project Overview

This project implements the functional requirements listed above using Java 17 and Maven.

Real implementation files will be created only when the LLM generates actual, meaningful code.
No dummy or placeholder test files are automatically created.

---
*Generated for {product_name}*
'''
