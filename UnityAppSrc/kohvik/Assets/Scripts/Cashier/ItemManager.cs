using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class ItemManager : MonoBehaviour
{
    [SerializeField] TMP_Text priceText;
    [SerializeField] TMP_Text prevOrderText;
    [SerializeField] private Image priceBG;
    [SerializeField] bool isMenu;
    [SerializeField] private Color discountedColor = Color.white;
    [SerializeField] private Color defaultColor = Color.white;
    public GameObject itemPrefab;
    public GameObject confirmBox;
    public GameObject messageBox;
    private TMP_Text messageBoxText;
    private TMP_Text confirmBoxText;
    private ItemList items;
    public static event Action OnResetCalled = null;
    private float price;
    private bool isMidOrder = false;
    private int itemCount;
    private int discountPercentage = 0;
    private string itemEndpoint = "getItems";
    private bool broughtOwnUtensils = false;
    private readonly static int utensilsDiscount = 10;
    public static ItemManager Instance { get; private set; }

    // Start is called before the first frame update
    void Start()
    {
        Instance = this;
        messageBoxText = messageBox.transform.GetChild(0).Find("MessageText").GetComponent<TMP_Text>();
        confirmBoxText = confirmBox.transform.GetChild(0).Find("ConfirmText").GetComponent<TMP_Text>();
        OnResetCalled += ResetPrice;
        if (isMenu)
        {
            itemEndpoint = "getMenuItems";
        }
        StartCoroutine(GetItems());
    }

    private IEnumerator GetItems()
    {
        UnityWebRequest www = UnityWebRequest.Get($"{Constants.IP}/{itemEndpoint}");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            string jsonResponse = www.downloadHandler.text;
            items = JsonUtility.FromJson<ItemList>("{\"Items\":" + jsonResponse + "}");
            foreach (Item item in items.Items)
            {
                GameObject go = Instantiate(itemPrefab, new Vector3(0, 0, 0), Quaternion.identity);
                go.transform.SetParent(transform, false);
                var child = go.GetComponent<ItemButton>();
                child.SetItem(item);
            }
        }
    }

    public void SetDiscount(int discount)
    {
        // TODO - expose discount to the UI
        if ((discount < 0) || (discount > 100))
        {
            Debug.Log("Invalid discount value!!!");
            return;
        }
        discountPercentage = discount;
        UpdatePriceText();
    }
    void ResetPrice()
    {
        price = 0;
        discountPercentage = 0;
        broughtOwnUtensils = false; // TODO - reset visual style too
        UpdatePriceText();
    }

    public void OnUtensilsToggled()
    {
        broughtOwnUtensils = !broughtOwnUtensils;
        SetDiscount(broughtOwnUtensils ? utensilsDiscount : 0);
        Debug.Log(broughtOwnUtensils);
        // TODO - change visual style
    }

    private float CalculatePrice()
    {
        return price / 100.0f * (100 - discountPercentage) / 100.0f;
    }
    void UpdatePriceText() {
        priceBG.color = discountPercentage > 0 ? discountedColor : defaultColor;
        priceText.text = string.Format("{0:0.00}€", CalculatePrice());
    }
    public void RemoveItemFromCart(Item item)
    {
        itemCount -= 1;
        price -= item.Price;
        UpdatePriceText();
    }

    public void AddItemToCart(Item item)
    {
        itemCount += 1;
        price += item.Price;
        UpdatePriceText();
    }

    public void OnResetPressed()
    {
        if (!isMidOrder)
        {
            OnResetCalled?.Invoke();
            Debug.Log("Reset!");
        }
    }

    public void OnOrderPressed()
    {
        if (itemCount > 0)
        {
            isMidOrder = true;
            messageBoxText.SetText($"Olete kindel, et soovite edastada tellimuse maksumusega {string.Format("{0:0.00}€?", CalculatePrice())}");
            messageBox.SetActive(true);
        }
    }

    public void AddOrder()
    {
        if (isMidOrder) {
            // Create a string to store the order data
            WWWForm form = new();
            // Loop through the items and append their ID and count to the order data

            form.AddField("discount", discountPercentage);
            foreach (var item in items.Items)
            {
                if (item.Count > 0)
                {
                    form.AddField(item.ID.ToString(), item.Count);
                }
            }
            // Start a coroutine to send the request asynchronously
            StartCoroutine(Upload(form));
            isMidOrder = false;
        }
        else
        {
            Debug.LogWarning("Tried to add order, but state is not mid order!");
        }
    }

    public void CancelOrder()
    {
        if (isMidOrder)
        {
            isMidOrder = false;
        }
        else
        {
            Debug.LogWarning("Tried to cancel order, but state is not mid order!");
        }
    }

    void SetPrevOrderText(string text)
    {
        prevOrderText.text = text;
    }
    IEnumerator Upload(WWWForm formData)
    {
        UnityWebRequest www = UnityWebRequest.Post($"{Constants.IP}/addOrder", formData);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
            SetPrevOrderText("Eelmine tellimus ebaõnnestus.");
            confirmBoxText.SetText("Tellimuse edastamine ebaõnnestus. Proovi uuesti ja/või kontrolli võrguühendust..");
        }
        else
        {
            string id = System.Text.Encoding.Default.GetString(www.downloadHandler.data);
            float currentPrice = CalculatePrice();
            SetPrevOrderText($"Eelmine tellimus {id.Trim()}: {string.Format("{0:0.00}€", currentPrice)}");
            confirmBoxText.SetText($"Tellimus {id.Trim()} edastatud, hind {string.Format("{0:0.00}€", currentPrice)}");
        }
        confirmBox.SetActive(true);
        www.Dispose();
        OnResetPressed();
    }




}
