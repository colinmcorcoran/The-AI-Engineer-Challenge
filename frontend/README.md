### Front End

## Running the Frontend (Next.js)

> Note: The frontend expects the backend to be running at `http://localhost:8000` and will POST to `/api/chat` with `{ message }`. Make sure the backend server is started and `OPENAI_API_KEY` is set in the backend environment.


1. Open a terminal and navigate to the `frontend` directory:

	```bash
	cd frontend
	```

2. Install dependencies:

	```bash
	npm install
	```

3. Start the development server:

	```bash
	npm run dev
	```

	The app will be available at [http://localhost:3000](http://localhost:3000).

4. To build for production:

	```bash
	npm run build
	npm start
	```

---

If you encounter errors, please copy and paste them into the Cursor chat for help!