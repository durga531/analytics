---
type: dashboard
---
# Home

## Due today or overdue
```tasks
not done
due before tomorrow
sort by due
```

## Open this week
```tasks
not done
path includes 02-Daily
sort by path reverse
limit 20
```

## Reviews due
```dataview
TABLE review_on AS "Review on", verdict AS "Verdict", status AS "Status"
WHERE review_on AND review_on <= date(today)
SORT review_on ASC
```

## Live engagements
```dataview
TABLE status AS "Status", updated AS "Updated"
FROM "03-Work"
WHERE type = "engagement"
SORT updated DESC
```

## Changed in the last seven days
```dataview
TABLE file.folder AS "Folder", file.mtime AS "Changed"
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 15
```

## Operating system
[[identity]] · [[active-areas]] · [[output-standards]] · [[thinking-patterns]] · [[templates]] · [[recurring-asks]] · [[Now]] · [[Lessons Queue]]

## Rhythm
Morning /today · Evening /close · Sunday /weekly · Inbox above ten /ingest · Anything that matters: FORGE: or /forge
