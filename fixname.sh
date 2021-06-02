#!/bin/sh

git filter-branch -f --env-filter '

OLD_NAME="sscottgvit"
OLD_EMAIL="sscottgvit@govanguard.com"
CORRECT_NAME="sscottgvit"
CORRECT_EMAIL="sscott@govanguard.com"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_NAME" = "$OLD_NAME" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_COMMITTER_NAME" = "$OLD_NAME" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
#if [ "$GIT_COMMITTER_NAME" != "$GIT_AUTHOR_NAME"  ]
#then
#    export GIT_AUTHOR_NAME="$GIT_COMMITTER_NAME"
#    export GIT_AUTHOR_EMAIL="$GIT_COMMITTER_EMAIL"
#fi
' --tag-name-filter cat -- --branches --tags

git push --force --tags origin 'refs/heads/*'
