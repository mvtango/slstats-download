#! /bin/bash
ssh -A werkzeugkasten 'bash -s' <<EOF
cd /srv/scribble-stat 
git pull
sudo service scribble restart
EOF

