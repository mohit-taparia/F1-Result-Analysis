all: instructions

instructions:
	latexmk -pdflatex -g -interaction=nonstopmode -outdir=build instructions.tex

# For live previewing on macOS with the Skim PDF reader
watch_instructions:
	latexmk -pdflatex -pvc -e '$$pdf_previewer=q[open -a Skim]' -outdir=build instructions.tex

# For live previewing on macOS with the Skim PDF reader
watch:
	latexmk -pdflatex -pvc -e '$$pdf_previewer=q[open -a Skim]' -outdir=build final_project.tex

clean:
	latexmk -C *.tex
