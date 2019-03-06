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

function getLastYumGetUpdate()
{
	releaseOutput=`cat /etc/os-release`
	if [[ ${releaseOutput} == *"Fedora"* ]]
		then
			local yumDate="$(stat -c %Y '/var/cache/dnf')"
	else
		local yumDate="$(stat -c %Y '/var/cache/yum')"
    fi 
	local nowDate="$(date +'%s')"

    echo $((nowDate - yumDate))
}

function runYumGetUpdate()
{
    local updateInterval="${1}"

    local lastYumGetUpdate="$(getLastYumGetUpdate)"

    if [[ "$(isEmptyString "${updateInterval}")" = 'true' ]]
    then
        # Default To 24 hours
        updateInterval="$((24 * 60 * 60))"
    fi

    if [[ "${lastYumGetUpdate}" -gt "${updateInterval}" ]]
    then
		if [[ ${releaseOutput} == *"Fedora"* ]]
			then
				info "dnf update"
				dnf update
		else
			info "yum update"
			yum update
			fi 
    else
        local lastUpdate="$(date -u -d @"${lastYumGetUpdate}" +'%-Hh %-Mm %-Ss')"

        info "\nSkip yum update because its last run was '${lastUpdate}' ago"
    fi
}
