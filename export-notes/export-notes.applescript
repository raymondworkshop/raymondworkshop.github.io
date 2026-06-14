on run argv
    set exportFile to item 1 of argv
    set checkDate to (current date) - (1 * days)
    set output to ""
    set noteCount to 0

    tell application "Notes"
        set recentNotes to every note whose modification date is greater than checkDate
        set noteCount to count of recentNotes
        repeat with aNote in recentNotes
            set noteTitle to name of aNote
            set noteText to plaintext of aNote
            set output to output & "---" & linefeed & "Title: " & noteTitle & linefeed & "---" & linefeed & noteText & linefeed & linefeed
        end repeat
    end tell

    if noteCount is 0 then return 0

    set fileRef to open for access (POSIX file exportFile) with write permission
    set eof of fileRef to 0
    write output to fileRef as «class utf8»
    close access fileRef

    return noteCount
end run
