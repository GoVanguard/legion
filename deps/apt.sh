function trimString()
{
    local -r string="${1}"

    sed -e 's/^ *//g' -e 's/ *$//g' <<< "${string}"
}

function isEmptyString()
{
    local -r string="${1}"

    if [[ "$(trimString "${string}")" = '' ]]
    then
        echo 'true'
    else
        echo 'false'
    fi
}

function info()
{
    local -r message="${1}"

    echo -e "\033[1;36m${message}\033[0m" 2>&1
}

function getLastAptGetUpdate()
{
    local aptDate="$(stat -c %Y '/var/cache/apt')"
    local nowDate="$(date +'%s')"

    echo $((nowDate - aptDate))
}

function runAptGetUpdate()
{
    local updateInterval="${1}"

    local lastAptGetUpdate="$(getLastAptGetUpdate)"

    if [[ "$(isEmptyString "${updateInterval}")" = 'true' ]]
    then
        # Default To 24 hours
        updateInterval="$((24 * 60 * 60))"
    fi

    if [[ "${lastAptGetUpdate}" -gt "${updateInterval}" ]]
    then
        info "apt-get update"
        apt-get update -m
    else
        local lastUpdate="$(date -u -d @"${lastAptGetUpdate}" +'%-Hh %-Mm %-Ss')"

        info "\nSkip apt-get update because its last run was '${lastUpdate}' ago"
    fi
}
