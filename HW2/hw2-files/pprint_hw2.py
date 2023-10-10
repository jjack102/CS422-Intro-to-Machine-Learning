import nbformat
import nbconvert.exporters as ex
import sys
import os.path

def write_template(template_file):

    template = r"""((*- extends 'article.tplx' -*))

%===============================================================================
% Input
%===============================================================================

((* block input scoped *))
   ((( custom_add_prompt(cell.source | wrap_text(88) | highlight_code(strip_verbatim=True), cell, 'In ', 'incolor') )))
((* endblock input *))

%===============================================================================
% Output
%===============================================================================

% Display stream ouput with coloring
((* block stream *))
    \begin{Verbatim}[commandchars=\\\{\},fontsize=\footnotesize]
((( output.text | wrap_text(86) | escape_latex | ansi2latex )))
    \end{Verbatim}
((* endblock stream *))

%==============================================================================
% Define macro custom_add_prompt() (derived from add_prompt() macro in style_ipython.tplx)
%==============================================================================

((* macro custom_add_prompt(text, cell, prompt, prompt_color) -*))
    ((*- if cell.execution_count is defined -*))
    ((*- set execution_count = "" ~ (cell.execution_count | replace(None, " ")) -*))
    ((*- else -*))
    ((*- set execution_count = " " -*))
    ((*- endif -*))
    ((*- set indention =  " " * (execution_count | length + 7) -*))
\begin{Verbatim}[commandchars=\\\{\},fontsize=\scriptsize]
((( text | add_prompts(first='{\color{' ~ prompt_color ~ '}' ~ prompt ~ '[{\\color{' ~ prompt_color ~ '}' ~ execution_count ~ '}]:} ', cont=indention) )))
\end{Verbatim}
((*- endmacro *))"""
    
    with open(template_file, 'w') as f:
        f.write(template)
    
def pprint(pdf_file, source_files):
        
    cells = []
    for filename in source_files:

        if not os.path.isfile(filename):
            sys.exit("Error: the required file " + filename + " is missing")

        if filename.endswith('.py'):
            with open(filename, 'r') as f:
                code_src = f.read()

            code_cell = nbformat.v4.new_code_cell(source=code_src, execution_count=1, outputs=[])

            if len(cells) > 0:
                cells += [nbformat.v4.new_markdown_cell( source = r'\newpage \setcounter{section}{0}' )]

            cells += [
                nbformat.v4.new_markdown_cell( source = '# CODE LISTING: ``' + filename + '``' ),
                code_cell
            ]

        elif filename.endswith('.ipynb'):

            this_notebook = nbformat.read(filename, 4)

            if len(cells) > 0:
                cells += [nbformat.v4.new_markdown_cell( source = r'\newpage \setcounter{section}{0}' )]

            cells += [nbformat.v4.new_markdown_cell( source = '# NOTEBOOK LISTING: ``' + filename + '``' )]
            cells += this_notebook.cells

        else:
            raise ValueError('Unrecognized format: ' + filename)

    # Export notebook
    notebook = nbformat.v4.new_notebook(cells=cells)

    # Converter
    pdf_exporter = ex.PDFExporter(latex_count=1)

    # Write template file to disk
    template_file = 'pdf.tplx'
    write_template(template_file)
    pdf_exporter.template_file = template_file

    # Convert
    output, resources = pdf_exporter.from_notebook_node(notebook)

    # Remove template file
    os.remove(template_file)
    
    # Write pdf contents to file
    with open(pdf_file, 'wb') as f:
        f.write(output)


pdf_file= 'hw2-code.pdf'
source_files = ['hw2.py', 'digit-classification.ipynb']

pprint(pdf_file, source_files)
