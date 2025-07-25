deploy:
	git stash
	git pull
	test -x ./deploy.sh || sudo chmod +x ./deploy.sh
	./deploy.sh