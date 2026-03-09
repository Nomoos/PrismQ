@echo off
:: run_all_32b.bat — Run all qwen3:32b pipeline steps (04, 08, 09)
:: Steps: content generation, title improvement, content improvement
:: Press Ctrl+C to stop the loop.

set SCRIPTS=C:\Users\hittl\PROJECTS\VideoMaking\PrismQ\_meta\scripts

:loop
echo.
echo [%time%] === 32b pass ===

call "%SCRIPTS%\04_PrismQ.T.Content.From.Idea.Title\Run.bat"
call "%SCRIPTS%\08_PrismQ.T.Title.From.Title.Review.Content\Run.bat"
call "%SCRIPTS%\09_PrismQ.T.Content.From.Title.Content.Review\Run.bat"

goto loop
