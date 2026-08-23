import re

with open("c:/Users/devan/OneDrive/Desktop/AE/Infacto/team.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. DELETE the duplicate chunk
# The duplicate chunk starts right after Outreach's Grid closing `</div>\n        </div>`
# Specifically, the string `<!-- Section: Delegate Affairs -->` appears TWICE.
# The second occurrence is the beginning of the garbage block. 
first_delegate = text.find('<!-- Section: Delegate Affairs -->')
second_delegate = text.find('<!-- Section: Delegate Affairs -->', first_delegate + 1)
treasurer = text.find('<!-- Section: Treasurer -->')

if second_delegate != -1 and treasurer != -1:
    # Delete everything from second_delegate up to Treasurer
    text = text[:second_delegate] + text[treasurer:]

# 2. Replace Samarth with Aryan in Outreach
# Grab Aryan's card from Execution or Marketing
aryan_match = re.search(r'(<div class="group relative bg-\[#0a0a0a\].*?Aryan Srivastava.*?</svg>\s*</a>\s*</div>\s*</div>\s*</div>)', text, re.DOTALL)
if aryan_match:
    aryan_card = aryan_match.group(1)
    # The subtitle on Aryan's card might be Marketing or Execution. Let's make it Outreach.
    aryan_card_outreach = re.sub(r'(<p class="text-emerald-500.*?uppercase mb-8"[^>]*>).*?(</p>)', r'\1Outreach\2', aryan_card)
    
    # Locate Outreach grid container specifically
    outreach_label = text.find('Outreach</span>')
    if outreach_label != -1:
        grid_div = text.find('<div class="mx-auto w-full grid', outreach_label)
        # Find the end of this *specific* grid div only
        grid_close = text.find('</div>\n        </div>', grid_div)
        
        if grid_div != -1 and grid_close != -1:
            outreach_content = text[grid_div:grid_close]
            # Replace whatever card is inside the grid (Samarth's card) with Aryan's card
            card_start = outreach_content.find('<div class="group relative')
            
            if card_start != -1:
                new_outreach_content = outreach_content[:card_start] + aryan_card_outreach + "\n            "
                text = text[:grid_div] + new_outreach_content + text[grid_close:]


with open("c:/Users/devan/OneDrive/Desktop/AE/Infacto/team.html", "w", encoding="utf-8") as f:
    f.write(text)

print("done")
