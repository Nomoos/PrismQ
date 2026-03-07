@echo off
:: run_all_14b.bat — Run all qwen3:14b pipeline steps (03, 05, 06, 07, 10-18)
:: Steps: title generation, all reviews
:: Press Ctrl+C to stop the loop.

set SCRIPTS=C:\Users\hittl\PROJECTS\VideoMaking\PrismQ\_meta\scripts

:loop
echo.
echo [%time%] === 14b pass ===

call "%SCRIPTS%\03_PrismQ.T.Title.From.Idea\Run.bat"
call "%SCRIPTS%\05_PrismQ.T.Review.Title.From.Content.Idea\Run.bat"
call "%SCRIPTS%\06_PrismQ.T.Review.Content.From.Title.Idea\Run.bat"
call "%SCRIPTS%\07_PrismQ.T.Review.Title.From.Content\Run.bat"
call "%SCRIPTS%\10_PrismQ.T.Review.Content.From.Title\Run.bat"
call "%SCRIPTS%\11_PrismQ.T.Review.Content.Grammar\Run.bat"
call "%SCRIPTS%\12_PrismQ.T.Review.Content.Tone\Run.bat"
call "%SCRIPTS%\13_PrismQ.T.Review.Content.Content\Run.bat"
call "%SCRIPTS%\14_PrismQ.T.Review.Content.Consistency\Run.bat"
call "%SCRIPTS%\15_PrismQ.T.Review.Content.Editing\Run.bat"
call "%SCRIPTS%\16_PrismQ.T.Review.Title.Readability\Run.bat"
call "%SCRIPTS%\17_PrismQ.T.Review.Content.Readability\Run.bat"
call "%SCRIPTS%\18_PrismQ.T.Story.Review\Run.bat"

goto loop
