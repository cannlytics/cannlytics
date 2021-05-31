# Donations

Cannlytics accepts donations and opted for [Stripe donations](https://stripe.com/docs/accepting-donations#go-live). If there is a better alternative, then please [let us know](https://cannlytics.com/contact).

If you want to setup donations for yourself, then these are the steps that we took.

[Register for Stripe](https://dashboard.stripe.com/register)

Get a Stripe test API key from the [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys).

Create a new file named `stripe.js` in `.admin/stripe` with the code:

```js

try {
  const stripe = require('stripe')('sk_test_51HbeVnCZbe0W4XE0jXtl5cgUM0efGcHRJgTW6XQ2DnhoIBXY9PUeSDAuNhS3YTdFG1AzeAczDOWeFYydB5WaNU9w00Is7jmzYt');
  const paymentIntent = await stripe.paymentIntents.create({
    amount: 1477, // $14.77, an easily identifiable amount
    currency: 'usd',
  });
  console.log('Worked! ', paymentIntent.id);
} catch(err) {
  console.log('Error! ', err.message);
}

```

