#!/bin/bash
version=$(grep "__version__" devo/__version__.py | cut -d'=' -f2 | tr -d '"' | xargs)
read -p "Bumping up version '$version'. Should we continue (Y/n)? " answer
case ${answer:0:1} in
    Y )
        echo "#### Bumping up for version '$version' ####"
    ;;
    * )
        exit 1
    ;;
esac
branch=$(git rev-parse --abbrev-ref HEAD)
echo "Git branch is '$branch'"
if [ "$branch" != "master" ]; then
    echo "Git branch should be 'master'"
    exit 2
fi
if /usr/bin/git ls-remote --exit-code origin refs/tags/v$version; then
    echo "Version '$version' already tagged in repo"
    exit 3
fi
last_changelog=$(grep -o "\[.*\]\s*\-\s*[0-9\-]*" CHANGELOG.md | head -n 1)
last_version=$(echo $last_changelog | cut -d']' -f1 | cut -d'[' -f2 | xargs)
last_date=$(echo $last_changelog | cut -d'-' -f2- | xargs)
echo "Last version in CHANGELOG.md is '$last_version' at '$last_date'"
if [ "$last_version" != "$version" ]; then
    echo "Last version in CHANGELOG.md '$last_version' does not match '$version'"
    exit 3
fi
today=$(date +%Y-%m-%d)
if [ "$last_date" != "$today" ]; then
    echo "Last version date in CHANGELOG.md '$last_date' does not match today '$today'"
    exit 3
fi
git tag -s "v$version" -m "v$version"
git push origin "v$version"