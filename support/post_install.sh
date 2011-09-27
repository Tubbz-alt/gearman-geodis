#! /bin/bash

# Add gearman_geodis user and group

if ! /usr/bin/id -g gearman_geodis &>/dev/null; then
	/usr/sbin/groupadd -r gearman_geodis
fi

if ! /usr/bin/id gearman_geodis &>/dev/null; then
	/usr/sbin/useradd -M -r -g gearman_geodis -s  /bin/false \
		-c "Gearman Geodis Worker" gearman_geodis > /dev/null 2>&1
fi

chown gearman_geodis:gearman_geodis /var/log/gearman_geodis
chown gearman_geodis:gearman_geodis /var/run/gearman_geodis
